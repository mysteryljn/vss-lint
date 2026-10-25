# vss-lint

离线检查 Vehicle Signal Specification（VSS）风格的车辆信号清单。输入是一个易于评审的 JSON 数组，检查路径命名、重复信号、描述、数据类型、单位和访问权限。

## 痛点

COVESA VSS 通过逻辑路径和统一语义抽象底层总线，但企业扩展、Overlay 和供应商字段很容易产生重复、含糊描述和单位不一致。本工具在提交前发现这些问题，不需要联网或 VSS 构建环境。

## 使用

    python vsslint.py examples/signals.json

## 许可证

MIT
