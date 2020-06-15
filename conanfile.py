from conans import ConanFile, CMake, tools
import os
import sys
"""
Debugging notes

linux:  (see https://github.com/conan-io/conan/issues/4736 for more details)
Setup gdb with .gdbinit to use the source mapping (see https://sourceware.org/gdb/current/onlinedocs/gdb/gdbinit-man.html for gdbinit details):

python
import os
if "SOURCE_MAP" in os.environ:
    for map in os.environ["SOURCE_MAP"].split(":"):
        if not "|" in map:
            continue
        gdb.execute("set substitute-path %s %s" % tuple(map.split("|")))
end
"""


class BcTrtisArmLibsConan(ConanFile):
    name = "trtis-third-party-arm"
    version = "trtis-arm-v1.12.0"
    license = "UNLICENSED"
    url = "https://github.com/TOVAMR/bc_conan_test.git"
    description = "external libraries for nvidia tis build for arm"
    topics = ("grpc" , "curl", "libevent", "libevhtp", "protobuf")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    default_user = "trtis"
    default_channel = "bc"

    # configuration where to take sources
    src_repo_url = "ssh://git@git-srv:2222/BriefCam/tensorrt-inference-server.git"

    def source(self):
        pos = self.version.find("-v")
        trtisVersion = self.version[pos + 1:]
        self.run(f"git clone --depth 1 --branch {trtisVersion} {self.src_repo_url} {self.source_folder}")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TRTIS_ENABLE_METRICS"]="OFF"
        cmake.definitions["TRTIS_ENABLE_TRACING"]="OFF"
        cmake.definitions["TRTIS_ENABLE_GCS"]="OFF"
        cmake.definitions["TRTIS_ENABLE_S3"]="OFF"
        cmake.definitions["TRTIS_ENABLE_CUSTOM"]="ON"
        cmake.definitions["TRTIS_ENABLE_TENSORFLOW"]="OFF"
        cmake.definitions["TRTIS_ENABLE_TENSORRT"]="OFF"
        cmake.definitions["TRTIS_ENABLE_CAFFE2"]="OFF"
        cmake.definitions["TRTIS_ENABLE_ONNXRUNTIME"]="OFF"
        cmake.definitions["TRTIS_ENABLE_ONNXRUNTIME_OPENVINO"]="OFF"
        cmake.definitions["TRTIS_ENABLE_HTTP"]="OFF"
        cmake.definitions["TRTIS_ENABLE_GPU"]="ON"
        cmake.definitions["TRTIS_ENABLE_PYTORCH"]="OFF"
        cmake.configure(source_folder="./build")        
        return cmake

    def build(self):
        cmake_release = self._configure_cmake()
        cmake_release.build(target='crc32c')
        cmake_release.build(target='grpc')
        cmake_release.build(target='libevhtp')
        cmake_release.build(target='curl')

    def _copyLib(self, libName, srcSubDir = ''):
        if (len(srcSubDir) != 0):
            srcSubDir = "/" + srcSubDir 

        self.copy("*", dst=libName + "/include", src= libName + srcSubDir + "/include", keep_path=True, symlinks=True)
        self.copy("*", dst=libName + "/bin"    , src= libName + srcSubDir + "/bin", keep_path=True, symlinks=True)
        self.copy("*", dst=libName + "/lib"    , src= libName + srcSubDir + "/lib", keep_path=True, symlinks=True)
        self.copy("*", dst=libName + "/src"    , src= "grpc-repo/src/grpc/third_party/" + libName , keep_path=True, symlinks=True)
        self.copy("*", dst=libName + "/src"    , src= "grpc-repo/src/grpc/src/" + libName , keep_path=True, symlinks=True)
        self.copy("*", dst=libName + "/src"    , src= libName + "/src/" + libName , keep_path=True, symlinks=True)

    def package(self):
        self._copyLib("grpc")
        self._copyLib("protobuf")
        self._copyLib("curl", "install")
        self._copyLib("c-ares")
        self._copyLib("libevent", "install")
        self._copyLib("libevhtp", "install")

    def package_info(self):
        pass

#self.cpp_info.libs = [""]
# gdb debugging
#self.env_info.CFLAGS.append("-fdebug-prefix-map=%s=%s" % (self.source_folder, self.name))
#self.env_info.CXXFLAGS.append("-fdebug-prefix-map=%s=%s" % (self.source_folder, self.name))
#self.env_info.SOURCE_MAP.append("%s|%s" % (self.name, os.path.join(self.package_folder, "src")))
