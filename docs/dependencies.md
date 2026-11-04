# Dependências observadas em 2026-11-01

Toolchain local, sem instalação com privilégios de administrador. As versões
e os hashes dos executáveis estão em [toolchain.json](../validation/toolchain.json).
GCC foi provisionado por micromamba/conda-forge; o runtime de libstdc++/libgcc
resolvido é 16.2.0, com compilador e headers de desenvolvimento 15.3.0.
Os binários carregam o runtime local de `.tools/gcc/lib`.

| Artefato baixado | SHA-256 |
| --- | --- |
| CMake 4.4.5 | `ed85135c5a5135b45e50423cb406dea04ca3338da0b8ef3c9ede963559680be0` |
| Ninja 1.13.2 | `5749cbc4e668273514150a80e387a957f933c6ed3f5f11e03fb30955e2bbead6` |
| Eigen 5.0.1 | `e9c326dc8c05cd1e044c71f30f1b2e34a6161a3b6ecf445d56b53ff1669e3dec` |
| nlohmann/json 3.12.0 | `42f6e95cad6ec532fd372391373363b62a14af6d771056dbfc86160e6dfff7aa` |
| Catch2 3.16.1 | `d16bd1b8b2364918bd472cb216394acb93bde6784890df0d91bccfb3f28d777d` |
| micromamba bootstrap | `9a97976244929bbae28fb1fae504e74a3e7e6d1932870e3a03321f01b7fbd07b` |
| LTspice MSI | `f22163f15420e43a2d5c66440e038ef031a9f019a181f396b95edcef5eebc357` |

Pacotes do compilador resolvidos:

| Pacote | Versão/build | SHA-256 do pacote |
| --- | --- | --- |
| _openmp_mutex | 4.5/20_gnu | `1dd3fffd892081df9726d7eb7e0dea6198962ba775bd88842135a4ddb4deb3c9` |
| binutils_impl_linux-64 | 2.46.1/default_hfdba357_103 | `98f9ddc6dc5d56a824b7eaea5bab6ad4bb47642288fc70d6b1b4024ac39d5595` |
| binutils_linux-64 | 2.46.1/default_h4852527_103 | `606a42c754752fb905fe2012d52ff370d47b5b6adefd5f7befc4ec30ce758f23` |
| gcc_impl_linux-64 | 15.3.0/h6ad849d_7 | `3c6deaf411a00aef601fb37f3a5e00aa4b85bace1fd2ebad347033aadc543c55` |
| gcc_linux-64 | 15.3.0/h7df7c86_2 | `0bb23a0685853c749490e9cd147da18397113c9ebb770f13363673b214012c86` |
| gxx_impl_linux-64 | 15.3.0/h90d9265_7 | `23e396ca14d05c645f431175379ec010676827d0b7791131ef4f1422f522a755` |
| gxx_linux-64 | 15.3.0/h39dd401_2 | `e2930d886fe946f7e15f79950d766911b4c523f354f6ce29b9b7f204bfa1fe91` |
| kernel-headers_linux-64 | 6.12.0/he073ed8_6 | `73b11f31db6c9ebe63d900334fa4f46859aa1ddd8f37cfa5f25a043e0a59253c` |
| ld_impl_linux-64 | 2.46.1/default_hbd61a6d_103 | `901649b1edbe841fd4ee7e2d491a05184ed540eb01cdae506872f344babc1d28` |
| libgcc | 16.2.0/ha9f2e26_7 | `e031634c3a928f9594eba868bc46ef5230d6571a364a0c63215b06c4563bfcea` |
| libgcc-devel_linux-64 | 15.3.0/h2b852eb_107 | `5200a1402eb3c3e9b0e4ba38b3cf163be136d020a15477fb86ce6e754d3ae515` |
| libgomp | 16.2.0/he0feb66_7 | `92a0bb350c7be6a4eedcb4e111c60aefd176018e6b1c009a6e025dbe9bbcd758` |
| libsanitizer | 15.3.0/h54950a5_7 | `9e5518e38502568f4591be965d48c1a3f79e2da4d74567f1a62e00244cf40222` |
| libstdcxx | 16.2.0/h934c35e_7 | `fa7018298629fc429971fffd6ecba3d27a7b02e4e890d6a93ea01ffebe8cb745` |
| libstdcxx-devel_linux-64 | 15.3.0/hb2c5482_107 | `4b2d94a9abf2feedea354e4256756c5dc255b84080e7faed9a324a101cf20e74` |
| libzlib | 1.3.2/h25fd6f3_3 | `eb8a0db0aa570124f7d2a93d7c7f596e3390df5e047818d873baad32985fc736` |
| sysroot_linux-64 | 2.39/hc4b9eeb_6 | `7d235e4337f122f3439d0196e1c1c6e715a5b88fcbf24f944510186c84168e45` |
| tzdata | 2026e/h5d301ff_0 | `2b7ca858879f183ce2dcc65b300f48a0133d5430550f35b23d80d405a0788dbf` |
| zstd | 1.5.7/hb78ec9c_7 | `47d682b9f6d6ec9eb1a6e6c3e75ea6273e899e78fb7fc59f81d39745009fbc60` |

Fontes: releases oficiais de [CMake](https://github.com/Kitware/CMake/releases/tag/v4.4.5),
[Ninja](https://github.com/ninja-build/ninja/releases/tag/v1.13.2),
[Eigen](https://gitlab.com/libeigen/eigen/-/releases/5.0.1),
[JSON](https://github.com/nlohmann/json/releases/tag/v3.12.0) e
[Catch2](https://github.com/catchorg/Catch2/releases/tag/v3.16.1).
Os arquivos de licença originais permanecem nas árvores em `.tools/deps`.
O LTspice 26.1.1 foi obtido do instalador MSI oficial da Analog Devices,
extraído por `msiexec /a /qn` para a pasta local do usuário Windows.
Não foi alterada a política de execução do PowerShell.

O ambiente Python usa CPython 3.14.4 padrão. Os dois locks foram resolvidos
com pip-tools 7.6.2 a partir de wheels compatíveis com este Linux x86-64/CPython.
São locks desta plataforma; não contêm hashes de todas as plataformas.
Para verificá-los com o wheelhouse já baixado:

```sh
.venv/bin/python -m pip install --no-index --find-links .tools/wheels --require-hashes -r validation/bootstrap-requirements.lock -r validation/requirements.lock
.venv/bin/python -m pip check
```

O bootstrap foi resolvido de `pip==26.2.2` e `pip-tools==7.6.2` com
`pip-compile --allow-unsafe --generate-hashes`; o ambiente analítico foi
resolvido de `validation/pyproject.toml`. O wheelhouse local limita a resolução
aos artefatos da plataforma selecionada. Downloads ocorreram somente durante
setup. spicelib e o restante da análise permanecem fora do núcleo C++.

A resolução de `files.pythonhosted.org` no WSL apresentou timeout. Durante
o bootstrap foi usado o endereço IPv4 retornado pelo DNS do Windows, sem
desabilitar TLS nem modificar configurações globais. Execuções normais não
dependem desse ajuste temporário.
