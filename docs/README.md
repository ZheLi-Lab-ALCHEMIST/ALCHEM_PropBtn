# ALCHEM_PropBtn 文档中心

📚 这里包含了 ALCHEM_PropBtn 项目的完整技术文档。

## 📋 文档索引

### 🚀 快速开始
- **[README.md](../README.md)** - 项目概述和快速开始
- **[CLAUDE.md](../CLAUDE.md)** - AI开发指导文档

### 🏗️ 技术文档
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 系统架构详细说明
- **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** - 开发者完整指南

### 📖 已整合的专项知识 (基于实际代码)
- **MolstarDisplayMixin架构** - 核心实现774行，示例427行，已完全集成
- **严格节点ID绑定系统** - WebSocket同步bug已修复，数据隔离完善
- **RDKit专业扩展** - 独立模块，5种编辑操作，智能格式检测
- **后端内存管理** - Tab感知内存599行实现，多Tab数据隔离
- **统一日志系统** - 前后端233行实现，表情符号标准化
- **WebSocket实时同步** - 279行实现，编辑和更新完全支持

## 🎯 文档使用指南

### 新手开发者
1. 阅读 [README.md](../README.md) 了解项目概况
2. 跟随 [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) 搭建开发环境
3. 查看 [ARCHITECTURE.md](./ARCHITECTURE.md) 理解系统设计

### 进阶开发者
1. 参考 [NODE_DEVELOPMENT_GUIDE.md](./NODE_DEVELOPMENT_GUIDE.md) 创建自定义节点
2. 使用 [LOGGING_STANDARDS.md](./LOGGING_STANDARDS.md) 规范化日志
3. 遵循 [CLEAN_ARCHITECTURE.md](./CLEAN_ARCHITECTURE.md) 保持代码质量

### AI辅助开发
- **[CLAUDE.md](../CLAUDE.md)** 为AI助手提供项目上下文和开发指导

## 🧪 项目特性

### 核心功能 (实际实现)
- 🧬 **分子文件处理** - 支持PDB/SDF/MOL/SMILES智能检测
- 🎯 **属性驱动架构** - 通过属性自动启用功能
- 🚀 **实时同步** - WebSocket实时数据同步 (279行实现)
- 🔧 **Tab感知内存** - 多Tab环境下的智能数据隔离 (599行实现)
- 🧪 **RDKit专业编辑** - 5种化学编辑操作，UFF力场优化

### 技术亮点 (基于实际代码)
- **方案B架构** - 节点主动数据获取模式 (355行molecular_utils)
- **🧪 MolstarDisplayMixin** - 774行核心实现，代码减少90%
- **严格节点ID绑定** - WebSocket同步bug已修复
- **RDKit专业扩展** - 独立模块，292行处理器+206行编辑器
- **模块化设计** - 松耦合的功能组件，完全隔离扩展
- **统一日志系统** - 233行实现，表情符号标准化

## 📞 支持和贡献

### 获取帮助
- 查看相关文档解决常见问题
- 使用内置调试工具进行问题排查
- 提交Issue报告Bug或请求新功能

### 贡献指南
- Fork项目仓库
- 创建功能分支
- 遵循项目代码规范
- 提交Pull Request

### 开发规范
- 使用统一的ALCHEM日志系统
- 遵循方案B架构模式
- 保持函数简洁（<50行）
- 严格的节点ID绑定