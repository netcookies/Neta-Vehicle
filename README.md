# Neta-Vehicle 集成插件 for Home Assistant

这是一个用于 Home Assistant 的自定义集成插件，允许用户通过 Home Assistant 平台监控和控制 Neta 电动汽车。该插件通过 Neta 车辆 API 获取车辆信息，如车辆状态、电池电量、充电状态等。

## 功能特性

- **实时车辆状态**：获取 Neta 车辆的实时信息，包括电池电量、充电状态、速度等。
- **充电状态监控**：监控车辆的充电状态。
- **位置追踪**：获取车辆的当前位置（如果支持）。
- **电池电量**：获取当前电池电量百分比。

## 系统要求

- Home Assistant 版本 2021.6 或更高。
- 已安装 HACS（Home Assistant Community Store）。
- 一辆已注册的 Neta 电动汽车，并且拥有 Neta API 访问凭证。

## 安装步骤

### 通过 HACS 安装

1. **安装插件**：
   - 打开 Home Assistant > HACS > 集成。
   - 搜索 "Neta Vehicle"。
   - 点击 "安装" 按钮安装该插件。

2. **配置插件**：
   - 安装完成后，进入 Home Assistant > 配置 > 集成。
   - 搜索并选择 "Neta Vehicle"。
   - 输入你的 Neta 车辆 API 凭证（可以通过 Neta 官方 API 获取或配置）。

### 手动安装

1. 将本仓库下载或克隆到 Home Assistant 的自定义组件目录：
   ```bash
   cd /config/custom_components
   git clone https://github.com/netcookies/Neta-Vehicle.git
   ```

2. 重启 Home Assistant。

3. 按照下面的配置步骤进行操作。

## 配置步骤

1. **进入集成设置**：
   - 打开 Home Assistant > 配置 > 集成。
   - 点击右下角的 “+ 添加集成” 按钮。

2. **搜索 Neta Vehicle**：
   - 在列表中选择 **Neta Vehicle** 集成。

3. **输入 API 凭证（token）**：
   - 系统会提示你输入 Neta 车辆的 API 凭证。这些凭证参考 **如何获取和更新 API 凭证（token）**。如果用小火箭获取token的话，可以先随便填一个。后面用小火箭更新

4. **保存配置**。

配置完成后，你就可以在 Home Assistant 中查看车辆信息，并使用它进行自动化或监控了。

## 使用说明

完成安装和配置后，该集成会暴露多个与车辆相关的实体。常见的实体包括：

- `sensor.neta_vehicle_battery_level`：显示 Neta 车辆的当前电池电量。
- `sensor.neta_vehicle_charging_status`：显示车辆是否正在充电。
- `sensor.neta_vehicle_location`：提供车辆的当前位置（如果支持）。
- `sensor.neta_vehicle_speed`：显示车辆的当前速度（如果支持）。

你可以将这些实体用于 Home Assistant 的自动化或监控。例如：

```yaml
automation:
  - alias: 当车辆电池电量低于 20% 时通知
    trigger:
      platform: numeric_state
      entity_id: sensor.neta_vehicle_battery_level
      below: 20
    action:
      service: notify.notify
      data:
        message: "Neta 车辆电池电量低于 20%。"
```

## 如何获取和更新 API 凭证（token）

### 有小火箭的情况（推荐）
1. 安装 [boxJs](https://docs.boxjs.app)
2. 在小火箭里添加 `https://gh-proxy.com/github.com/netcookies/Neta-Vehicle/blob/main/scripts/getAppToken.sgmodule`
3. 在小火箭连接的情况下，打开浏览器输入网址 `https://boxjs.com`
4. 添加订阅 `https://gh-proxy.com/github.com/netcookies/Neta-Vehicle/raw/refs/heads/main/boxjs.json`
5. 获取 **Homeassistant Access Token**，在homeassistant - 个人设置 - 安全 - 长期访问令牌
6. 打开boxjs的哪吒汽车应用，添加 **API 地址** `https://{此处填你自己的homeassistant服务器 IP}/api/services/neta_vehicle/update_token`和**Homeassistant Access Token**。
7. **Neta Vehicle Token**可以先空着或随便填一个
8. 打开小火箭连接开关，同时在哪吒汽车的 app 里刷新下，就可以自动获取到**Neta Vehicle Token**了。

### 没小火箭的情况，请自行搜索手机抓包教程
- 抓包获取 Response Header的 Authorization字段， 值类似：`Bearer eyJhbGciOxxxxxxxxx`,其中 `eyJhbGciOxxxxxxxxx`就是**Neta Vehicle Token**


## 常见问题与故障排除

- 请确保你输入的 Neta API 凭证是正确的。
- 确保 Home Assistant 能访问 Neta 车辆 API。
- 如果集成没有显示数据，请检查 Home Assistant 日志，查看是否有相关的错误信息。

如果遇到问题，您可以查看该仓库的 [Issues](https://github.com/netcookies/Neta-Vehicle/issues) 部分，或提交新问题。

## 贡献

如果你希望为这个项目做出贡献，欢迎 Fork 本仓库并提交 Pull Request。请确保你的代码符合现有的编码风格，并且有适当的文档说明。

## 许可证

本项目使用 MIT 许可证，详情请见 [LICENSE](LICENSE) 文件。

---

### 代码分析

#### 关键文件

1. **`__init__.py`**：这个文件包含了集成的初始化代码，负责管理集成生命周期，如加载配置、初始化车辆信息等。
2. **`manifest.json`**：定义了插件的元数据，如名称、版本、依赖项等。
3. **`vehicle.py`**：通常包含与车辆的交互逻辑，如如何获取车辆状态、发送 API 请求等。
4. **`sensor.py`**：定义了 Home Assistant 的传感器实体，用于暴露车辆的信息（例如电池电量、位置等）。
5. **`config_flow.py`**：如果集成支持通过 UI 流式配置（如输入 API 密钥），该文件负责处理配置流程。
