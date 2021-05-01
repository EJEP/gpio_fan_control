DROP TABLE IF EXISTS temp_and_speed;

CREATE TABLE temp_and_speed(
measurement_time DATETIME,
cpu_temp NUMERIC,
cpu_temp_1_minute NUMERIC,
cpu_temp_5_minute NUMERIC,
cpu_temp_10_minute NUMERIC,
sensor_temp NUMERIC,
sensor_temp_1_minute NUMERIC,
sensor_temp_5_minute NUMERIC,
sensor_temp_10_minute NUMERIC,
current_duty_cycle NUMERIC,
next_duty_cycle NUMERIC
);

CREATE INDEX idx_temp_speed_time ON temp_and_speed (measurement_time);
