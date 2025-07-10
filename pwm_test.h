/*

 * Copyright (c) 2006-2021, RT-Thread Development Team
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Change Logs:
 * Date           Author       Notes
 * 2025-06-25     lenovo       the first version
 * 2025-06-27     Added PID control for 4 motors
 * 2025-06-28     Added speed synchronization
 * 2025-06-30     Added dual PWM control for direction
 * 2025-07-01     Fixed backward direction to use backward PWM channel
 * 2025-07-04     Added backward calibration factor
 * 2025-07-05     Added motor direction enum for clarity
*/
/*
#ifndef PWM_TEST_H_
#define PWM_TEST_H_

#include <rtthread.h>
#include <rtdevice.h>
#include <drivers/pulse_encoder.h>
#include <stdlib.h>
#include <math.h>

#define PWM_PERIOD_NS  20000000   // PWM周期20ms (50Hz)

 //电机方向枚举
typedef enum {
    MOTOR_STOP = 0,
    MOTOR_FORWARD = 1,
    MOTOR_BACKWARD = -1
} motor_direction_t;

 //PID控制器结构体
typedef struct {
    float Kp;
    float Ki;
    float Kd;
    float integral;
    float prev_error;
    float output;
    float max_output;
    float min_output;
} pid_controller_t;

 //电机控制器结构体
typedef struct {
    rt_device_t enc_dev;  // 编码器设备句柄
    const char *pwm_forward_dev_name;   // 前进PWM设备名
    const char *pwm_backward_dev_name;  // 后退PWM设备名
    struct rt_device_pwm *pwm_forward_dev;   // 前进PWM设备句柄
    struct rt_device_pwm *pwm_backward_dev;  // 后退PWM设备句柄
    int pwm_forward_channel;   // 前进PWM通道
    int pwm_backward_channel;  // 后退PWM通道
    int ppr;                   // 编码器每转脉冲数
    float calibration_factor;  // 前进校准因子
    float calibration_factor_backward; // 后退校准因子
    pid_controller_t pid;      // PID控制器
    rt_int32_t target_speed;   // 目标速度 (RPM)
    rt_int32_t actual_speed;   // 实际速度 (RPM)
} motor_controller_t;

 //全局变量
extern motor_controller_t motor_ctrl[4];

// 函数声明
void pid_init(pid_controller_t *pid, float Kp, float Ki, float Kd, float min, float max);
float pid_compute(pid_controller_t *pid, float setpoint, float input);
void set_motor_direction_speed(int motor_id, int direction, rt_int32_t duty_ns);
void set_motor_speed_per_channel(int motor_id, rt_uint32_t duty_ns);
void set_motor_speed(rt_uint32_t duty_ns);
void set_motor_target_speed(int motor_id, int speed_rpm);
void set_all_motors_target_speed(int speed_rpm);
void calibrate_motor_speeds(void);
int motor_pwm_init(void);

#endif  PWM_TEST_H_*/

/* pwm_test.h */
#ifndef __PWM_TEST_H__
#define __PWM_TEST_H__

#include <rtthread.h>

void init_all_motors(void);
void stop_all_motors(void);
void set_left_motors_speed(int speed);
void set_right_motors_speed(int speed);
void set_all_motors_speed(int speed);

#endif /* __PWM_TEST_H__ */

