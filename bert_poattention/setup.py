# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Simple check list from AllenNLP repo: https://github.com/allenai/allennlp/blob/master/setup.py

To create the package for pypi.

1. Change the version in __init__.py, setup.py as well as docs/source/conf.py. Remove the master from the links in
   the new models of the README:
   (https://huggingface.co/transformers/master/model_doc/ -> https://huggingface.co/transformers/model_doc/)
   then run `make fix-copies` to fix the index of the documentation.

2. Unpin specific versions from setup.py that use a git install.

2. Commit these changes with the message: "Release: VERSION"

3. Add a tag in git to mark the release: "git tag VERSION -m'Adds tag VERSION for pypi' "
   Push the tag to git: git push --tags origin master

4. Build both the sources and the wheel. Do not change anything in setup.py between
   creating the wheel and the source distribution (obviously).

   For the wheel, run: "python setup.py bdist_wheel" in the top level directory.
   (this will build a wheel for the python version you use to build it).

   For the sources, run: "python setup.py sdist"
   You should now have a /dist directory with both .whl and .tar.gz source versions.

5. Check that everything looks correct by uploading the package to the pypi test server:

   twine upload dist/* -r pypitest
   (pypi suggest using twine as other methods upload files via plaintext.)
   You may have to specify the repository url, use the following command then:
   twine upload dist/* -r pypitest --repository-url=https://test.pypi.org/legacy/

   Check that you can install it in a virtualenv by running:
   pip install -i https://testpypi.python.org/pypi transformers

6. Upload the final version to actual pypi:
   twine upload dist/* -r pypi

7. Copy the release notes from RELEASE.md to the tag in github once everything is looking hunky-dory.

8. Add the release version to docs/source/_static/js/custom.js and .circleci/deploy.sh

9. Update README.md to redirect to correct documentation.

10. Update the version in __init__.py, setup.py to the new version "-dev" and push to master.
"""

import os
import re
import shutil
from distutils.core import Command
from pathlib import Path

from setuptools import find_packages, setup


# Remove stale transformers.egg-info directory to avoid https://github.com/pypa/pip/issues/5466
stale_egg_info = Path(__file__).parent / "transformers.egg-info"
if stale_egg_info.exists():
    print(
        (
            "Warning: {} exists.\n\n"
            "If you recently updated transformers to 3.0 or later, this is expected,\n"
            "but it may prevent transformers from installing in editable mode.\n\n"
            "This directory is automatically generated by Python's packaging tools.\n"
            "I will remove it now.\n\n"
            "See https://github.com/pypa/pip/issues/5466 for details.\n"
        ).format(stale_egg_info)
    )
    shutil.rmtree(stale_egg_info)


# IMPORTANT:
# 1. all dependencies should be listed here with their version requirements if any
# 2. once modified, run: `make deps_table_update` to update src/transformers/dependency_versions_table.py
_deps = [
    "black>=20.8b1",
    "cookiecutter==1.7.2",
    "dataclasses",
    "datasets",
    "faiss-cpu",
    "fastapi",
    "filelock",
    "flake8>=3.8.3",
    "flax>=0.2.2",
    "fugashi>=1.0",
    "importlib_metadata",
    "ipadic>=1.0.0,<2.0",
    "isort>=5.5.4",
    "jax>=0.2.0",
    "jaxlib==0.1.55",
    "keras2onnx",
    "numpy",
    "onnxconverter-common",
    "onnxruntime-tools>=1.4.2",
    "onnxruntime>=1.4.0",
    "packaging",
    "parameterized",
    "protobuf",
    "psutil",
    "pydantic",
    "pytest",
    "pytest-xdist",
    "python>=3.6.0",
    "recommonmark",
    "regex!=2019.12.17",
    "requests",
    "sacremoses",
    "scikit-learn",
    "sentencepiece==0.1.91",
    "sphinx-copybutton",
    "sphinx-markdown-tables",
    "sphinx-rtd-theme==0.4.3",  # sphinx-rtd-theme==0.5.0 introduced big changes in the style.
    "sphinx==3.2.1",
    "starlette",
    "tensorflow-cpu>=2.3",
    "tensorflow>=2.3",
    "timeout-decorator",
    "tokenizers==0.9.4",
    "torch>=1.0",
    "tqdm>=4.27",
    "unidic>=1.0.2",
    "unidic_lite>=1.0.7",
    "uvicorn",
]


# tokenizers: "tokenizers==0.9.4" lookup table
# support non-versions file too so that they can be checked at run time
deps = {b: a for a, b in (re.findall(r"^(([^!=<>]+)(?:[!=<>].*)?$)", x)[0] for x in _deps)}


def deps_list(*pkgs):
    return [deps[pkg] for pkg in pkgs]


class DepsTableUpdateCommand(Command):
    """
    A custom distutils command that updates the dependency table.
    usage: python setup.py deps_table_update
    """

    description = "build runtime dependency table"
    user_options = [
        # format: (long option, short option, description).
        ("dep-table-update", None, "updates src/transformers/dependency_versions_table.py"),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        entries = "\n".join([f'    "{k}": "{v}",' for k, v in deps.items()])
        content = [
            "# THIS FILE HAS BEEN AUTOGENERATED. To update:",
            "# 1. modify the `_deps` dict in setup.py",
            "# 2. run `make deps_table_update``",
            "deps = {",
            entries,
            "}",
            "",
        ]
        target = "src/transformers/dependency_versions_table.py"
        print(f"updating {target}")
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(content))


extras = {}

extras["ja"] = deps_list("fugashi", "ipadic", "unidic_lite", "unidic")
extras["sklearn"] = deps_list("scikit-learn")

extras["tf"] = deps_list("tensorflow", "onnxconverter-common", "keras2onnx")
extras["tf-cpu"] = deps_list("tensorflow-cpu", "onnxconverter-common", "keras2onnx")

extras["torch"] = deps_list("torch")

if os.name == "nt":  # windows
    extras["retrieval"] = deps_list("datasets")  # faiss is not supported on windows
    extras["flax"] = []  # jax is not supported on windows
else:
    extras["retrieval"] = deps_list("faiss-cpu", "datasets")
    extras["flax"] = deps_list("jax", "jaxlib", "flax")

extras["tokenizers"] = deps_list("tokenizers")
extras["onnxruntime"] = deps_list("onnxruntime", "onnxruntime-tools")
extras["modelcreation"] = deps_list("cookiecutter")

extras["serving"] = deps_list("pydantic", "uvicorn", "fastapi", "starlette")

extras["sentencepiece"] = deps_list("sentencepiece", "protobuf")
extras["retrieval"] = deps_list("faiss-cpu", "datasets")
extras["testing"] = (
    deps_list("pytest", "pytest-xdist", "timeout-decorator", "parameterized", "psutil")
    + extras["retrieval"]
    + extras["modelcreation"]
)
extras["docs"] = deps_list("recommonmark", "sphinx", "sphinx-markdown-tables", "sphinx-rtd-theme", "sphinx-copybutton")
extras["quality"] = deps_list("black", "isort", "flake8")

extras["all"] = extras["tf"] + extras["torch"] + extras["flax"] + extras["sentencepiece"] + extras["tokenizers"]

extras["dev"] = (
    extras["all"]
    + extras["testing"]
    + extras["quality"]
    + extras["ja"]
    + extras["docs"]
    + extras["sklearn"]
    + extras["modelcreation"]
)


# when modifying the following list, make sure to update src/transformers/dependency_versions_check.py
install_requires = [
    deps["dataclasses"] + ";python_version<'3.7'",  # dataclasses for Python versions that don't have it
    deps["importlib_metadata"] + ";python_version<'3.8'",  # importlib_metadata for Python versions that don't have it
    deps["filelock"],  # filesystem locks, e.g., to prevent parallel downloads
    deps["numpy"],
    deps["packaging"],  # utilities from PyPA to e.g., compare versions
    deps["regex"],  # for OpenAI GPT
    deps["requests"],  # for downloading models over HTTPS
    deps["sacremoses"],  # for XLM
    deps["tokenizers"],
    deps["tqdm"],  # progress bars in model download and training scripts
]

setup(
    name="transformers",
    version="4.2.0.dev0", # expected format is one of x.y.z.dev0, or x.y.z.rc1 or x.y.z (no to dashes, yes to dots)
    author="Thomas Wolf, Lysandre Debut, Victor Sanh, Julien Chaumond, Sam Shleifer, Patrick von Platen, Sylvain Gugger, Google AI Language Team Authors, Open AI team Authors, Facebook AI Authors, Carnegie Mellon University Authors",
    author_email="thomas@huggingface.co",
    description="State-of-the-art Natural Language Processing for TensorFlow 2.0 and PyTorch",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="NLP deep learning transformer pytorch tensorflow BERT GPT GPT-2 google openai CMU",
    license="Apache",
    url="https://github.com/huggingface/transformers",
    package_dir={"": "src"},
    packages=find_packages("src"),
    extras_require=extras,
    entry_points={"console_scripts": ["transformers-cli=transformers.commands.transformers_cli:main"]},
    python_requires=">=3.6.0",
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    cmdclass={"deps_table_update": DepsTableUpdateCommand},
)
