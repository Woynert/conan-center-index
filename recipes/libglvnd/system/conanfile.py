from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.50.0"


class ConanGTK(ConanFile):
    name = "libglvnd"
    description = "The GL Vendor-Neutral Dispatch library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/glvnd/libglvnd"
    topics = ("dispatch", "egl", "gl", "gles", "glx", "glvnd", "opengl", "vendor-neutral")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "shared-library"

    def package_id(self):
        self.info.settings.clear()

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    # TODO
    # def system_requirements(self):
        # dnf = package_manager.Dnf(self)
        # dnf.install([f"gtk{self.options.version}-devel"], update=True, check=True)

        # yum = package_manager.Yum(self)
        # yum.install([f"gtk{self.options.version}-devel"], update=True, check=True)

        # apt = package_manager.Apt(self)
        # apt.install(["libgtk2.0-dev"] if self.options.version == 2 else ["libgtk-3-dev"], update=True, check=True)

        # pacman = package_manager.PacMan(self)
        # pacman.install([f"gtk{self.options.version}"], update=True, check=True)

        # zypper = package_manager.Zypper(self)
        # zypper.install([f"gtk{self.options.version}-devel"], update=True, check=True)

        # pkg = package_manager.Pkg(self)
        # pkg.install([f"gtk{self.options.version}"], update=True, check=True)

    def package_info(self):
        for name in ["egl", "gl", "glesv1_cm", "glesv2", "glx", "libglvnd", "opengl"]:
            pkg_config = PkgConfig(self, name)
            pkg_config.fill_cpp_info(
                self.cpp_info.components[name], is_system=self.settings.os != "FreeBSD")
            self.cpp_info.components[name].set_property(
               "pkg_config_name", name)
