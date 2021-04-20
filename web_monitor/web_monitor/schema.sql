DROP TABLE IF EXISTS temp_and_speed;

CREATE TABLE temp_and_speed(
measurement_time DATETIME,
cpu_temp NUMERIC,
sensor_temp NUMERIC,
current_duty_cycle NUMERIC,
next_duty_cycle NUMERIC
);
