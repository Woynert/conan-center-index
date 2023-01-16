import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, chdir, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class LibcapConan(ConanFile):
    name = "libcap"
    license = ("GPL-2.0-only", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/libs/libcap/libcap.git"
    description = "This is a library for getting and setting POSIX.1e" \
                  " (formerly POSIX 6) draft 15 capabilities"
    topics = ("capabilities")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "psx_syscals": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "psx_syscals": False,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.info.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def layout(self):
        basic_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.fpic = self.options.get_safe("fPIC", True)
        env = tc.environment()
        env.define("SHARED", "yes" if self.options.shared else "no")
        env.define("PTHREADS", "yes" if self.options.psx_syscals else "no")
        env.define("DESTDIR", self.package_folder)
        env.define("prefix", "/")
        env.define("lib", "lib")

        if cross_building(self) and not env.vars(self).get("BUILD_CC"):
            native_cc = VirtualBuildEnv(self).vars().get("CC")
            if not native_cc:
                native_cc = "cc"
            self.output.info(f"Using native compiler '{native_cc}'")
            env.define("BUILD_CC", native_cc)

        tc.generate(env)

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        with chdir(self, os.path.join(self.source_folder, self.name)):
            autotools.make()

    def package(self):
        copy(self, "License", self.source_folder,
             os.path.join(self.package_folder, "licenses"), keep_path=False)

        autotools = Autotools(self)
        with chdir(self, os.path.join(self.source_folder, self.name)):
            autotools.make(target="install-common-cap")
            install_cap = ("install-shared-cap" if self.options.shared
                           else "install-static-cap")
            autotools.make(target=install_cap)

            if self.options.psx_syscals:
                autotools.make(target="install-common-psx")
                install_psx = ("install-shared-psx" if self.options.shared
                               else "install-static-psx")
                autotools.make(target=install_psx)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["cap"].set_property("pkg_config_name",
                                                     "libcap")
        self.cpp_info.components["cap"].names["pkg_config"] = "libcap"
        self.cpp_info.components["cap"].libs = ["cap"]
        if self.options.psx_syscals:
            self.cpp_info.components["psx"].set_property("pkg_config_name",
                                                         "libpsx")
            self.cpp_info.components["psx"].names["pkg_config"] = "libpsx"
            self.cpp_info.components["psx"].libs = ["psx"]
            self.cpp_info.components["psx"].system_libs = ["pthread"]
            self.cpp_info.components["psx"].exelinkflags = [
                "-Wl,-wrap,pthread_create"]
