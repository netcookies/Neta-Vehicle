## chargingStatus - 充电状态相关

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| power_charge_status             | 充电状态                           | 0        |
| power_charge_time               | 充电时间                           | 未充电时：65,534，充电时值为剩余时间  |
| obc_elect_wire_con_light_sts    | OBC 电气连接状态                   | 0        |
| obc_charge_voltage              | OBC 充电电压                       | 0        |
| obc_charge_voltage_inp          | OBC 输入充电电压                   | 0        |
| obc_charge_current              | OBC 充电电流                       | 3        |
| obc_charge_current_inp          | OBC 输入充电电流                   | 0        |
| obc_cm_state                    | OBC CM 状态                        | 7        |

## vehicleBasic - 车辆基本状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| dc_status                       | 直流状态                           | 2        |
| total_current                   | 总电流                             | 10,000   |
| charge_status                   | 充电状态                           | 3        |
| total_voltage                   | 总电压                             | 3,586    |
| run_mode                        | 行驶模式                           | 1        |
| speed                           | 车速                               | 0        |
| gears                           | 变速状态                           | 15       |
| vehicle_status                  | 车辆状态                           | 2        |

## enduranceStatus - 续航状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| power_percentage                | 电池电量百分比                     | 8,200    |
| power_residue_mileage           | 剩余电量里程                       | 1,930    |
| estimate_fuel_level             | 估算油量水平                       | 7        |
| bms_battery_total_capacity      | BMS 电池总容量                     | 11,800   |
| estimate_fuel_percent           | 估算油量百分比                     | 15       |
| bms_hds_ah_active_cp_sum        | BMS HDS AH 活跃电量总和             | 11,712   |
| fuel_mileage_remaining          | 剩余油量里程                       | 1,170    |

## vehicleExtend - 车辆扩展信息

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| cellular_net_status             | 移动网络状态                       | 3        |
| battery_12_voltage              | 12V 电池电压                       | 125      |
| bat_electricity                 | 电池电量                           | 10,000   |
| cellular_net_db                 | 移动网络信号强度                   | 4        |
| motor_status                    | 电机状态                           | 3        |
| drive_mode                      | 驾驶模式                           | 3        |
| bat_voltage                     | 电池电压                           | 3,586    |
| position_status                 | 车辆定位状态                       | 0        |
| engine_status                   | 发动机状态                         | 0        |
| gps_status                      | GPS 状态                           | 1        |
| battery_size                    | 电池大小                           | 1        |
| latitude                        | 纬度                               | 26.05    |
| longitude                       | 经度                               | 119.36   |

## energyConsumption - 能耗信息

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| today_energy_consumption        | 今日能量消耗                       | 65,535   |
| total_average_consumption_rate  | 总平均能量消耗率                   | 11,880   |
| itinerary_driving_mileage       | 行程驾驶里程                       | 177      |
| average_consumption_per_km      | 每公里平均能量消耗                 | 11,700   |
| trip_consumes_energy            | 行程消耗的能量                     | 65,535   |
| itinerary_duration              | 行程时长                           | 1,980    |

## vehicleConnection - 车辆连接状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| online                          | 是否在线                           | true     |
| online_status                   | 在线状态                           | 3        |
| report_time                     | 上报时间                           | 1,744,072,942,000 |
| last_change_time                | 最后变更时间                       | 未知     |

## lampStatus - 灯光状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| small_light_status              | 小灯状态                           | 0        |
| brake_beam_light_status        | 刹车灯状态                         | 0        |
| high_beam_light_status          | 高光灯状态                         | 0        |
| right_turn_light_status         | 右转灯状态                         | 0        |
| double_flash_light_status       | 双闪灯状态                         | 0        |
| left_turn_light_status          | 左转灯状态                         | 0        |
| mood_light_status               | 氛围灯状态                         | 255      |
| dipped_head_light_status        | 近光灯状态                         | 0        |

## seatStatus - 座椅状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| left_after_seat_heating_status  | 左后座座椅加热状态                 | 0        |
| right_after_seat_ventilation_status | 右后座座椅通风状态               | 0        |
| driver_folding_seat_status      | 驾驶座折叠座椅状态                 | 255      |
| right_after_seat_heating_status | 右后座座椅加热状态                 | 0        |
| left_after_seat_ventilation_status | 左后座座椅通风状态               | 0        |
| co_driver_seat_ventilation_status | 副驾座椅通风状态                  | 0        |
| co_driver_folding_seat_status   | 副驾座椅折叠状态                   | 255      |
| co_driver_seat_heating_status   | 副驾座椅加热状态                   | 0        |
| driver_seat_ventilation_status  | 驾驶座座椅通风状态                 | 0        |
| driver_seat_heating_status      | 驾驶座座椅加热状态                 | 0        |

## doorCoverStatus - 车门/盖状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| cover_front_status              | 前舱盖状态                         | 0        |
| slow_charge_cover_status       | 慢充口盖状态                       | 0        |
| left_after_door_status         | 左后门状态                         | 0        |
| driver_size_door_status        | 主驾门状态                         | 0        |
| co_driver_size_door_status     | 副驾门状态                         | 0        |
| fuel_tank_cover_status         | 油箱盖状态                         | 0        |
| fast_charge_cover_status       | 快充口盖状态                       | 0        |
| right_after_door_status        | 右后门状态                         | 0        |
| car_boar_status                | 后备箱状态                         | 0        |

## airconditionStatus - 空调系统

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| clm_vent_sts                    | 通风状态                           | 0        |
| defrost_status                  | 除霜状态                           | 0        |
| air_filter_element              | 空调滤芯状态                       | 0        |
| thermal_container_status        | 热管理容器状态                     | 0        |
| air_temp                        | 空调设定温度                       | 24       |
| air_wind_level                  | 风速等级                           | 3        |
| lock_car_keep_status            | 锁车维持状态                       | 0        |
| air_out_temp                    | 出风口温度                         | 23       |
| air_in_temp                     | 进风口温度                         | 22       |
| thermal_container_temp          | 热容器温度                         | 40       |
| clm_foot_sts                    | 脚部送风状态                       | 0        |
| air_mode                        | 空调模式（自动、手动等）           | 1        |
| clm_ac_sts                      | 压缩机状态                         | 0        |
| air_status                      | 空调开关状态                       | 1        |

## windowStatus - 车窗状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| driver_size_win_status          | 驾驶员侧窗状态                     | 16       |
| sky_window_status               | 天窗状态                           | 0        |
| right_after_win_lock_status     | 右后窗锁状态                       | 16       |
| left_after_win_status           | 左后窗状态                         | 16       |
| co_driver_size_win_status       | 副驾驶侧窗状态                     | 16       |

## tyreStatus - 胎压与胎温

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| tire_right_after_press          | 右后轮胎气压                       | 136      |
| tire_right_front_press          | 右前轮胎气压                       | 138      |
| tire_left_front_press           | 左前轮胎气压                       | 138      |
| tire_right_front_temp           | 右前轮胎温度                       | 78       |
| tire_left_after_temp            | 左后轮胎温度                       | 77       |
| tire_left_front_temp            | 左前轮胎温度                       | 78       |
| tire_right_after_temp           | 右后轮胎温度                       | 77       |
| tire_left_after_press           | 左后轮胎气压                       | 136      |

## lockStatus - 锁状态

| 字段名称                        | 含义                               | 参考值   |
|---------------------------------|------------------------------------|----------|
| co_driver_size_door_lock_status | 副驾驶侧门锁状态                   | 0        |
| slow_charge_cover_lock_status  | 慢充盖锁状态                       | 0        |
| driver_size_door_lock_status   | 驾驶员侧门锁状态                   | 0        |
| car_boar_lock_status           | 车厢盖锁状态                       | 0        |
| left_after_door_lock_status    | 左后门锁状态                       | 0        |
| fast_charge_cover_lock_status  | 快充盖锁状态                       | 0        |
| right_after_door_lock_status   | 右后门锁状态                       | 0        |
| fuel_tank_cover_lock_status    | 油箱盖锁状态                       | 0        |
