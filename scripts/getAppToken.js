const $ = API("netavehicle", false); // 初始化 BoxJs
const hass_token = $.read("hass_access_token"); // 读取 Home Assistant 访问 Token
const hass_url = $.read("hass_api_url"); // 读取 Home Assistant API 地址
const oldTokenVal = $.read("token"); // 读取本地存储的旧 Token

const tokenName = "NetaVehicle";
const authHeaderKey = Object.keys($request.headers).find(k => k.toLowerCase() === "authorization");
let tokenVal = authHeaderKey ? $request.headers[authHeaderKey].replace("Bearer ", "") : null;

// 记录调试信息
$.log(`[INFO] 处理 Token 更新`);
$.log(`tokenName: ${tokenName}`);
$.log(`新 Token: ${tokenVal}`);
$.log(`旧 Token: ${oldTokenVal}`);
$.log(`hass_token: ${hass_token ? "存在" : "未找到"}`);
$.log(`hass_url: ${hass_url || "未设置"}`);

if (tokenVal && tokenVal !== oldTokenVal) {
    $.write(tokenVal, "token"); // 更新存储的 Token
    $.notify(tokenName, "Token 写入成功", `新 Token: ${tokenVal}`);

    if (hass_url && hass_token) {
        const headers = {
            "Authorization": `Bearer ${hass_token}`,
            "Content-Type": "application/json"
        };
        const body = JSON.stringify({ token: tokenVal });

        // 发送 API 请求
        $.http.post({ url: hass_url, headers, body }).then(response => {
            $.log(`[INFO] Home Assistant 响应头: ${JSON.stringify(response.headers)}`);
            $.notify("NetaVehicle 更新成功", "✅ Token 已更新", `新 Token: ${tokenVal}`);
        }).catch(error => {
            $.log(`[ERROR] API 请求失败: ${error}`);
            $.notify("NetaVehicle 更新失败", "❌ API 请求错误", error);
        });
    } else {
        $.notify("NetaVehicle 更新失败", "❌ Home Assistant 配置缺失", "请检查 hass_url 和 hass_token 设置");
    }
}

$.done();
