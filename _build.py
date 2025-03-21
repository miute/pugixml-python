from __future__ import annotations

import os
import subprocess
import sys
from logging import INFO
from pathlib import Path
from typing import Any

import tomli  # TODO: Use tomlib instead of tomli.
from setuptools import Extension
from setuptools.command.build_ext import build_ext

# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}


class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        Extension.__init__(self, name, sources=[])
        self.root = Path(__file__).parent.resolve()
        self.sourcedir = self.root / sourcedir


class CMakeBuild(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        extdir = (ext.root / self.get_ext_fullpath(ext.name)).parent / ext.name

        env = os.environ.copy()
        cmake_build_type = env.get("CMAKE_BUILD_TYPE", "Release")
        cfg = "Debug" if self.debug else cmake_build_type

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
            "-Wno-dev",
        ]
        build_args = []

        cmake_generator = env.get("CMAKE_GENERATOR")
        is_msbuild = self.compiler.compiler_type == "msvc" and (
            cmake_generator is None
            or cmake_generator.startswith("Visual Studio")
        )
        is_multi_config = is_msbuild or cmake_generator in [
            "Ninja Multi-Config",
            "Xcode",
        ]

        if is_multi_config:
            cmake_args += [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}",
            ]
            build_args += [
                "--config",
                cfg,
            ]

        if is_msbuild and "CMAKE_GENERATOR_PLATFORM" not in env:
            cmake_args += [
                "-A",
                PLAT_TO_CMAKE[self.plat_name],
            ]

        if (
            "CMAKE_BUILD_PARALLEL_LEVEL" not in env
            and not is_msbuild
            and (
                cmake_generator is None
                or not cmake_generator.startswith("Ninja")
            )
        ):
            jobs = (
                hasattr(self, "parallel") and self.parallel
            ) or os.cpu_count()
            if jobs:
                build_args += [
                    "-j",
                    str(jobs),
                ]

        self.announce(
            f"-- CXX environment variable: {env.get('CXX')!r}",
            level=INFO,
        )
        self.announce(
            f"-- CXXFLAGS environment variable: {env.get('CXXFLAGS')!r}",
            level=INFO,
        )
        self.announce(
            "-- CMake environment variables: {!r}".format(
                [
                    f"{k}={v}"
                    for k, v in env.items()
                    if k.upper().startswith("CMAKE")
                ]
            ),
            level=INFO,
        )
        self.announce(
            f"-- CMake build system options: {cmake_args!r}", level=INFO
        )
        self.announce(f"-- CMake build options: {build_args!r}", level=INFO)

        build_temp = ext.root / self.build_temp / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)
        self.announce(f"-- Working directory: {build_temp!r}", level=INFO)

        subprocess.check_call(  # noqa: S603
            ["cmake", ext.sourcedir, *cmake_args],  # noqa: S607
            cwd=build_temp,
            env=env,
        )
        subprocess.check_call(  # noqa: S603
            ["cmake", "--build", ".", *build_args],  # noqa: S607
            cwd=build_temp,
        )


def build(setup_kwargs: dict[str, Any]) -> None:
    here = Path(__file__).parent.resolve()
    with open(here / "pyproject.toml", "rb") as f:
        md = tomli.load(f)
        setup_kwargs.update(
            {
                "ext_modules": [CMakeExtension(md["project"]["name"], "src")],
                "cmdclass": {"build_ext": CMakeBuild},
            }
        )
