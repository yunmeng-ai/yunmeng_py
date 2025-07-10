
 //添加头文件
#include <stdlib.h>
#include <math.h>
#include <stm32f4xx.h>  // 修复hal_cortex.h报错*/


 /* Copyright (c) 2006-2021, RT-Thread Development Team
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
 * 2025-07-04     Added support for negative duty cycle (backward)
 * 2025-07-05     Optimized reverse motor control for smoother operation*/


#define DBG_TAG "pwm_test.c"
#define DBG_LVL DBG_LOG
#include <rtdbg.h>
#include "pwm_test.h"
#include <pulse.h>
#include <rtthread.h>
#include <rtdevice.h>

#define PULSE_ENCODER_CMD_GET_DIRECTION 0x20
#define PWM_PERIOD_NS  20000000

// 全局变量
rt_int32_t common_target_speed = 0;

 //全局电机控制器实例
motor_controller_t motor_ctrl[4] = {
    // M1 (左侧)
    {.enc_dev = RT_NULL,
     .pwm_forward_dev_name = "pwm1", .pwm_forward_channel = 4,
     .pwm_backward_dev_name = "pwm1", .pwm_backward_channel = 3,
     .ppr = 400, .calibration_factor = 1.0f, .calibration_factor_backward = 1.0f},

    // M2 (左侧)
    {.enc_dev = RT_NULL,
     .pwm_forward_dev_name = "pwm1", .pwm_forward_channel = 2,
     .pwm_backward_dev_name = "pwm1", .pwm_backward_channel = 1,
     .ppr = 400, .calibration_factor = 1.0f, .calibration_factor_backward = 1.0f},

    // M3 (右侧)
    {.enc_dev = RT_NULL,
     .pwm_forward_dev_name = "pwm9", .pwm_forward_channel = 2,
     .pwm_backward_dev_name = "pwm9", .pwm_backward_channel = 1,
     .ppr = 400, .calibration_factor = 1.0f, .calibration_factor_backward = 1.0f},

    // M4 (右侧)
    {.enc_dev = RT_NULL,
     .pwm_forward_dev_name = "pwm10", .pwm_forward_channel = 1,
     .pwm_backward_dev_name = "pwm11", .pwm_backward_channel = 1,
     .ppr = 400, .calibration_factor = 1.0f, .calibration_factor_backward = 1.0f}
};

 //PID初始化函数
void pid_init(pid_controller_t *pid, float Kp, float Ki, float Kd, float min, float max)
{
    pid->Kp = Kp;
    pid->Ki = Ki;
    pid->Kd = Kd;
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->output = 0.0f;
    pid->max_output = max;
    pid->min_output = min;
}

// PID计算函数
float pid_compute(pid_controller_t *pid, float setpoint, float input)
{
    float error = setpoint - input;
    float proportional = pid->Kp * error;

    pid->integral += error;
    if (pid->integral > pid->max_output) pid->integral = pid->max_output;
    if (pid->integral < pid->min_output) pid->integral = pid->min_output;
    float integral = pid->Ki * pid->integral;

    float derivative = pid->Kd * (error - pid->prev_error);
    pid->prev_error = error;

    pid->output = proportional + integral + derivative;

    if (pid->output > pid->max_output) pid->output = pid->max_output;
    if (pid->output < pid->min_output) pid->output = pid->min_output;

    return pid->output;
}

 //设置电机方向和速度 - 支持负占空比
void set_motor_direction_speed(int motor_id, int direction, rt_int32_t duty_ns)
{
    if (duty_ns > PWM_PERIOD_NS) duty_ns = PWM_PERIOD_NS;
    if (duty_ns < -PWM_PERIOD_NS) duty_ns = -PWM_PERIOD_NS;

    if (motor_id < 1 || motor_id > 4) {
        LOG_E("Invalid motor ID: %d", motor_id);
        return;
    }

    int idx = motor_id - 1;
    struct rt_device_pwm *forward_dev = motor_ctrl[idx].pwm_forward_dev;
    struct rt_device_pwm *backward_dev = motor_ctrl[idx].pwm_backward_dev;

    const char *fwd_name = motor_ctrl[idx].pwm_forward_dev_name;
    const char *bwd_name = motor_ctrl[idx].pwm_backward_dev_name;

    if (!forward_dev || !backward_dev) {
        LOG_E("PWM device not initialized for motor %d", motor_id);
        return;
    }

    /*LOG_D("Set Motor%d: Dir=%d, Duty=%dns, F_Dev=%s:%d, B_Dev=%s:%d",
          motor_id, direction, duty_ns,
          fwd_name, motor_ctrl[idx].pwm_forward_channel,
          bwd_name, motor_ctrl[idx].pwm_backward_channel);*/

    switch (direction) {
        case 0: // 停止
            rt_pwm_set(forward_dev, motor_ctrl[idx].pwm_forward_channel, PWM_PERIOD_NS, 0);
            rt_pwm_set(backward_dev, motor_ctrl[idx].pwm_backward_channel, PWM_PERIOD_NS, 0);
            break;
        case 1: // 前进
            rt_pwm_set(forward_dev, motor_ctrl[idx].pwm_forward_channel, PWM_PERIOD_NS, (rt_uint32_t)duty_ns);
            rt_pwm_set(backward_dev, motor_ctrl[idx].pwm_backward_channel, PWM_PERIOD_NS, 0);
            break;
        case -1: // 后退
            rt_pwm_set(forward_dev, motor_ctrl[idx].pwm_forward_channel, PWM_PERIOD_NS, 0);
            rt_pwm_set(backward_dev, motor_ctrl[idx].pwm_backward_channel, PWM_PERIOD_NS, (rt_uint32_t)(-duty_ns));
            break;
        default:
            LOG_E("Invalid direction: %d for motor %d", direction, motor_id);
            break;
    }
}

 //设置单个电机的PWM占空比（兼容旧接口）
void set_motor_speed_per_channel(int motor_id, rt_uint32_t duty_ns)
{
    set_motor_direction_speed(motor_id, 1, (rt_int32_t)duty_ns);
}

 //设置所有电机的PWM占空比
void set_motor_speed(rt_uint32_t duty_ns)
{
    if (duty_ns > PWM_PERIOD_NS) duty_ns = PWM_PERIOD_NS;

    for (int i = 1; i <= 4; i++) {
        set_motor_direction_speed(i, 1, (rt_int32_t)duty_ns);
    }
}

 //设置单个电机目标速度
void set_motor_target_speed(int motor_id, int speed_rpm)
{
    if (motor_id >= 1 && motor_id <= 4) {
        motor_ctrl[motor_id-1].target_speed = speed_rpm;
        LOG_I("Motor %d target speed set to %d RPM", motor_id, speed_rpm);
    } else {
        LOG_E("Invalid motor ID: %d", motor_id);
    }
}

 //设置所有电机目标速度
void set_all_motors_target_speed(int speed_rpm)
{
    common_target_speed = speed_rpm;
    for (int i = 0; i < 4; i++) {
        motor_ctrl[i].target_speed = speed_rpm;
    }
    LOG_I("All motors target speed set to %d RPM", speed_rpm);
}

 //编码器读取线程
static void encoder_thread_entry(void *parameter)
{
    while (1)
    {
        for (int i = 0; i < 4; i++)
        {
            if (motor_ctrl[i].enc_dev) {
                rt_int32_t count = 0;
                rt_device_read(motor_ctrl[i].enc_dev, 0, &count, sizeof(count));

                if (motor_ctrl[i].ppr > 0) {
                    float rpm = (count / (float)motor_ctrl[i].ppr) * (60.0f / 0.1f);
                    if (count >= 0) {
                        motor_ctrl[i].actual_speed = (rt_int32_t)(rpm * motor_ctrl[i].calibration_factor);
                    } else {
                        // 确保实际速度为负值
                        motor_ctrl[i].actual_speed = (rt_int32_t)(-fabs(rpm) * motor_ctrl[i].calibration_factor_backward);
                    }
                } else {
                    motor_ctrl[i].actual_speed = 0;
                }

                rt_device_control(motor_ctrl[i].enc_dev, PULSE_ENCODER_CMD_CLEAR_COUNT, RT_NULL);
            }
        }
        rt_thread_mdelay(100);
    }
}

 //PID控制线程 - 支持负占空比
static void pid_thread_entry(void *parameter)
{
    while (1)
    {
        for (int i = 0; i < 4; i++)
        {
            if (motor_ctrl[i].target_speed != 0 && motor_ctrl[i].enc_dev)
            {
                float pid_out = pid_compute(&motor_ctrl[i].pid,
                                          motor_ctrl[i].target_speed,
                                          motor_ctrl[i].actual_speed);

                // 根据目标速度符号决定方向
                int direction = (motor_ctrl[i].target_speed >= 0) ? 1 : -1;

                // 计算占空比（支持负值）
                rt_int32_t duty = (rt_int32_t)(PWM_PERIOD_NS * fabs(pid_out) / 100.0f) * (direction);

                set_motor_direction_speed(i+1, direction, duty);

                LOG_D("Motor%d: Target:%d RPM, Actual:%d RPM, PID out:%.1f, PWM:%d ns",
                      i+1, motor_ctrl[i].target_speed,
                      motor_ctrl[i].actual_speed, pid_out, duty);
            }
            else if (motor_ctrl[i].target_speed == 0) {
                set_motor_direction_speed(i+1, 0, 0);
            }
        }
        rt_thread_mdelay(20);
    }
}

 //校准电机速度 - 分别校准前进和后退
void calibrate_motor_speeds(void)
{
    LOG_I("Starting motor calibration...");

    // 前进校准
    for (int i = 1; i <= 4; i++) {
        set_motor_direction_speed(i, 1, PWM_PERIOD_NS * 50 / 100);
    }
    rt_thread_mdelay(3000);

    rt_int32_t avg_forward_speed = 0;
    rt_int32_t forward_speeds[4] = {0};

    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 4; j++) {
            if (motor_ctrl[j].enc_dev) {
                rt_int32_t count = 0;
                rt_device_read(motor_ctrl[j].enc_dev, 0, &count, sizeof(count));
                rt_device_control(motor_ctrl[j].enc_dev, PULSE_ENCODER_CMD_CLEAR_COUNT, RT_NULL);

                float rpm = (count / (float)motor_ctrl[j].ppr) * (60.0f / 0.1f);
                forward_speeds[j] += (rt_int32_t)rpm;
            }
        }
        rt_thread_mdelay(100);
    }

    // 后退校准
    for (int i = 1; i <= 4; i++) {
        set_motor_direction_speed(i, -1, PWM_PERIOD_NS * 50 / 100);
    }
    rt_thread_mdelay(3000);

    rt_int32_t avg_backward_speed = 0;
    rt_int32_t backward_speeds[4] = {0};

    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 4; j++) {
            if (motor_ctrl[j].enc_dev) {
                rt_int32_t count = 0;
                rt_device_read(motor_ctrl[j].enc_dev, 0, &count, sizeof(count));
                rt_device_control(motor_ctrl[j].enc_dev, PULSE_ENCODER_CMD_CLEAR_COUNT, RT_NULL);

                float rpm = (count / (float)motor_ctrl[j].ppr) * (60.0f / 0.1f);
                // 累加绝对值确保速度为正
                backward_speeds[j] += (rt_int32_t)fabs(rpm);
            }
        }
        rt_thread_mdelay(100);
    }

    // 计算平均速度
    for (int j = 0; j < 4; j++) {
        forward_speeds[j] /= 10;
        backward_speeds[j] /= 10;
        avg_forward_speed += forward_speeds[j];
        avg_backward_speed += backward_speeds[j];
    }
    avg_forward_speed /= 4;
    avg_backward_speed /= 4;

    // 设置校准因子
    for (int j = 0; j < 4; j++) {
        if (forward_speeds[j] > 0) {
            motor_ctrl[j].calibration_factor = (float)avg_forward_speed / forward_speeds[j];
            LOG_I("Motor%d Forward: Measured:%d RPM, Calib:%.3f",
                  j+1, forward_speeds[j], motor_ctrl[j].calibration_factor);
        }

        if (backward_speeds[j] > 0) {
            motor_ctrl[j].calibration_factor_backward = (float)avg_backward_speed / backward_speeds[j];
            LOG_I("Motor%d Backward: Measured:%d RPM, Calib:%.3f",
                  j+1, backward_speeds[j], motor_ctrl[j].calibration_factor_backward);
        }
    }

    // 停止电机
    for (int i = 1; i <= 4; i++) {
        set_motor_direction_speed(i, 0, 0);
    }
    LOG_I("Motor calibration completed!");
}

// PWM初始化函数
int motor_pwm_init(void)
{
    rt_err_t ret = RT_EOK;

    // 初始化PWM设备
    for (int i = 0; i < 4; i++) {
        // 初始化前进PWM设备
        motor_ctrl[i].pwm_forward_dev = (struct rt_device_pwm *)rt_device_find(motor_ctrl[i].pwm_forward_dev_name);
        if (!motor_ctrl[i].pwm_forward_dev) {
            LOG_E("Forward PWM device %s not found for motor %d",
                  motor_ctrl[i].pwm_forward_dev_name, i+1);
        } else {
            rt_pwm_set(motor_ctrl[i].pwm_forward_dev,
                      motor_ctrl[i].pwm_forward_channel,
                      PWM_PERIOD_NS, 0);
            rt_pwm_enable(motor_ctrl[i].pwm_forward_dev,
                         motor_ctrl[i].pwm_forward_channel);
        }

        // 初始化后退PWM设备
        motor_ctrl[i].pwm_backward_dev = (struct rt_device_pwm *)rt_device_find(motor_ctrl[i].pwm_backward_dev_name);
        if (!motor_ctrl[i].pwm_backward_dev) {
            LOG_E("Backward PWM device %s not found for motor %d",
                  motor_ctrl[i].pwm_backward_dev_name, i+1);
        } else {
            rt_pwm_set(motor_ctrl[i].pwm_backward_dev,
                      motor_ctrl[i].pwm_backward_channel,
                      PWM_PERIOD_NS, 0);
            rt_pwm_enable(motor_ctrl[i].pwm_backward_dev,
                         motor_ctrl[i].pwm_backward_channel);
        }
    }

     //初始化编码器设备
    const char *encoder_names[] = {"pulse5", "pulse2", "pulse4", "pulse3"};
    for (int i = 0; i < 4; i++) {
        motor_ctrl[i].enc_dev = rt_device_find(encoder_names[i]);
        if (!motor_ctrl[i].enc_dev) {
            LOG_E("Encoder device %s not found for motor %d!", encoder_names[i], i+1);
        } else {
            ret = rt_device_open(motor_ctrl[i].enc_dev, RT_DEVICE_OFLAG_RDONLY);
            if (ret != RT_EOK) {
                LOG_E("Failed to open encoder %s for motor %d", encoder_names[i], i+1);
                motor_ctrl[i].enc_dev = RT_NULL;
            } else {
                rt_device_control(motor_ctrl[i].enc_dev, PULSE_ENCODER_CMD_CLEAR_COUNT, RT_NULL);
            }
        }
        if (!motor_ctrl[i].pwm_backward_dev) {
            LOG_E("Backward PWM init FAIL! Motor:%d Dev:%s",
                  i+1, motor_ctrl[i].pwm_backward_dev_name);
            motor_ctrl[i].pwm_backward_dev = (struct rt_device_pwm *)rt_device_find(motor_ctrl[i].pwm_backward_dev_name);
            if(motor_ctrl[i].pwm_backward_dev) {
                rt_pwm_enable(motor_ctrl[i].pwm_backward_dev,
                             motor_ctrl[i].pwm_backward_channel);
            }
        }
    }

     //初始化PID控制器
    for (int i = 0; i < 4; i++) {
        pid_init(&motor_ctrl[i].pid, 0.8f, 0.2f, 0.05f, 0.0f, 100.0f);
        motor_ctrl[i].target_speed = 0;
    }

    // 创建编码器读取线程
    rt_thread_t enc_thread = rt_thread_create("encoder",
                                           encoder_thread_entry,
                                           RT_NULL,
                                           1024,
                                           15,
                                           10);
    if (enc_thread) {
        rt_thread_startup(enc_thread);
        LOG_I("Encoder thread started");
    } else {
        LOG_E("Failed to create encoder thread");
    }

    // 创建PID控制线程
    rt_thread_t pid_thread = rt_thread_create("pid_ctrl",
                                            pid_thread_entry,
                                            RT_NULL,
                                            2048,
                                            10,
                                            10);
    if (pid_thread) {
        rt_thread_startup(pid_thread);
        LOG_I("PID control thread started");
    } else {
        LOG_E("Failed to create PID thread");
    }

     //执行电机校准
    calibrate_motor_speeds();

    LOG_I("PWM and encoders initialized successfully!");
    return RT_EOK;
}
INIT_APP_EXPORT(motor_pwm_init);

 //测试命令：设置占空比百分比（支持负值）
static void pwm_test(int argc, char **argv)
{
    if (argc != 2)
    {
        rt_kprintf("Usage: pwm_set [duty(-100 to 100)]\n");
        return;
    }

    int duty_percent = atoi(argv[1]);
    if (duty_percent < -100 || duty_percent > 100)
    {
        rt_kprintf("Invalid duty! (-100 to 100)\n");
        return;
    }

    int direction = (duty_percent >= 0) ? 1 : -1;
    rt_uint32_t duty_ns = PWM_PERIOD_NS * abs(duty_percent) / 100;

    for (int i = 1; i <= 4; i++) {
        set_motor_direction_speed(i, direction, (rt_int32_t)duty_ns);
    }

    rt_kprintf("Set all motors: %s, PWM duty: %d%% -> %dns\n",
              (direction == 1) ? "FORWARD" : "BACKWARD",
              abs(duty_percent), duty_ns);
}

 //设置单个电机目标速度命令
static void set_speed(int argc, char **argv)
{
    if (argc != 3)
    {
        rt_kprintf("Usage: set_speed [motor_id(1-4)] [speed_rpm]\n");
        return;
    }

    int motor_id = atoi(argv[1]);
    int speed_rpm = atoi(argv[2]);

    set_motor_target_speed(motor_id, speed_rpm);
}

 //设置所有电机目标速度命令
static void set_all_speed(int argc, char **argv)
{
    if (argc != 2)
    {
        rt_kprintf("Usage: set_all_speed [speed_rpm]\n");
        return;
    }

    int speed_rpm = atoi(argv[1]);
    set_all_motors_target_speed(speed_rpm);
}

 //调整PID参数命令
static void set_pid(int argc, char **argv)
{
    if (argc != 5)
    {
        rt_kprintf("Usage: set_pid [motor_id(1-4|0=all)] [Kp] [Ki] [Kd]\n");
        return;
    }

    int motor_id = atoi(argv[1]);
    float Kp = atof(argv[2]);
    float Ki = atof(argv[3]);
    float Kd = atof(argv[4]);

    if (motor_id == 0) {
        for (int i = 0; i < 4; i++) {
            pid_init(&motor_ctrl[i].pid, Kp, Ki, Kd, 0.0f, 100.0f);
        }
        rt_kprintf("Set all motors PID: Kp=%.2f, Ki=%.2f, Kd=%.2f\n", Kp, Ki, Kd);
    }
    else if (motor_id >= 1 && motor_id <= 4) {
        pid_init(&motor_ctrl[motor_id-1].pid, Kp, Ki, Kd, 0.0f, 100.0f);
        rt_kprintf("Set motor %d PID: Kp=%.2f, Ki=%.2f, Kd=%.2f\n", motor_id, Kp, Ki, Kd);
    }
    else {
        rt_kprintf("Invalid motor ID: %d\n", motor_id);
    }
}

 //重新校准电机命令
static void recalibrate(int argc, char **argv)
{
    calibrate_motor_speeds();
}

MSH_CMD_EXPORT(set_speed, Set motor target speed in RPM);
MSH_CMD_EXPORT(set_all_speed, Set all motors target speed in RPM);
MSH_CMD_EXPORT(set_pid, Set PID parameters for motor(s));
MSH_CMD_EXPORT(recalibrate, Recalibrate motor speeds);
MSH_CMD_EXPORT(pwm_test, Set PWM duty cycle);

