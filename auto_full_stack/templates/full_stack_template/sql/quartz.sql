DROP TABLE IF EXISTS QRTZ_FIRED_TRIGGERS;
DROP TABLE IF EXISTS QRTZ_PAUSED_TRIGGER_GRPS;
DROP TABLE IF EXISTS QRTZ_SCHEDULER_STATE;
DROP TABLE IF EXISTS QRTZ_LOCKS;
DROP TABLE IF EXISTS QRTZ_SIMPLE_TRIGGERS;
DROP TABLE IF EXISTS QRTZ_SIMPROP_TRIGGERS;
DROP TABLE IF EXISTS QRTZ_CRON_TRIGGERS;
DROP TABLE IF EXISTS QRTZ_BLOB_TRIGGERS;
DROP TABLE IF EXISTS QRTZ_TRIGGERS;
DROP TABLE IF EXISTS QRTZ_JOB_DETAILS;
DROP TABLE IF EXISTS QRTZ_CALENDARS;

-- ----------------------------
-- 1. Stores details for each configured JobDetail
-- ----------------------------
create table QRTZ_JOB_DETAILS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    job_name             varchar(200)    not null            comment 'Job name',
    job_group            varchar(200)    not null            comment 'Job group name',
    description          varchar(250)    null                comment 'Description',
    job_class_name       varchar(250)    not null            comment 'Job implementation class name',
    is_durable           varchar(1)      not null            comment 'Whether the job is durable',
    is_nonconcurrent     varchar(1)      not null            comment 'Whether concurrent execution is disallowed',
    is_update_data       varchar(1)      not null            comment 'Whether job data should be updated after execution',
    requests_recovery    varchar(1)      not null            comment 'Whether recovery execution is requested',
    job_data             blob            null                comment 'Serialized persistent JobDataMap',
    primary key (sched_name, job_name, job_group)
) engine=innodb comment = 'Job detail table';

-- ----------------------------
-- 2. Stores configured trigger information
-- ----------------------------
create table QRTZ_TRIGGERS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    trigger_name         varchar(200)    not null            comment 'Trigger name',
    trigger_group        varchar(200)    not null            comment 'Trigger group name',
    job_name             varchar(200)    not null            comment 'Foreign key to qrtz_job_details.job_name',
    job_group            varchar(200)    not null            comment 'Foreign key to qrtz_job_details.job_group',
    description          varchar(250)    null                comment 'Description',
    next_fire_time       bigint(13)      null                comment 'Next fire time in milliseconds',
    prev_fire_time       bigint(13)      null                comment 'Previous fire time in milliseconds',
    priority             integer         null                comment 'Priority',
    trigger_state        varchar(16)     not null            comment 'Trigger state',
    trigger_type         varchar(8)      not null            comment 'Trigger type',
    start_time           bigint(13)      not null            comment 'Start time',
    end_time             bigint(13)      null                comment 'End time',
    calendar_name        varchar(200)    null                comment 'Calendar name',
    misfire_instr        smallint(2)     null                comment 'Misfire handling instruction',
    job_data             blob            null                comment 'Serialized persistent JobDataMap',
    primary key (sched_name, trigger_name, trigger_group),
    foreign key (sched_name, job_name, job_group) references QRTZ_JOB_DETAILS(sched_name, job_name, job_group)
) engine=innodb comment = 'Trigger detail table';

-- ----------------------------
-- 3. Stores simple triggers, including repeat count, interval, and times triggered
-- ----------------------------
create table QRTZ_SIMPLE_TRIGGERS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    trigger_name         varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_name',
    trigger_group        varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_group',
    repeat_count         bigint(7)       not null            comment 'Repeat count',
    repeat_interval      bigint(12)      not null            comment 'Repeat interval',
    times_triggered      bigint(10)      not null            comment 'Number of times triggered',
    primary key (sched_name, trigger_name, trigger_group),
    foreign key (sched_name, trigger_name, trigger_group) references QRTZ_TRIGGERS(sched_name, trigger_name, trigger_group)
) engine=innodb comment = 'Simple trigger table';

-- ----------------------------
-- 4. Stores Cron triggers, including Cron expressions and time zones
-- ---------------------------- 
create table QRTZ_CRON_TRIGGERS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    trigger_name         varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_name',
    trigger_group        varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_group',
    cron_expression      varchar(200)    not null            comment 'Cron expression',
    time_zone_id         varchar(80)                         comment 'Time zone',
    primary key (sched_name, trigger_name, trigger_group),
    foreign key (sched_name, trigger_name, trigger_group) references QRTZ_TRIGGERS(sched_name, trigger_name, trigger_group)
) engine=innodb comment = 'Cron trigger table';

-- ----------------------------
-- 5. Stores custom Trigger implementations as BLOBs when JobStore cannot persist them directly
-- ---------------------------- 
create table QRTZ_BLOB_TRIGGERS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    trigger_name         varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_name',
    trigger_group        varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_group',
    blob_data            blob            null                comment 'Serialized persistent Trigger object',
    primary key (sched_name, trigger_name, trigger_group),
    foreign key (sched_name, trigger_name, trigger_group) references QRTZ_TRIGGERS(sched_name, trigger_name, trigger_group)
) engine=innodb comment = 'BLOB trigger table';

-- ----------------------------
-- 6. Stores calendar information as BLOBs for defining scheduling time ranges
-- ---------------------------- 
create table QRTZ_CALENDARS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    calendar_name        varchar(200)    not null            comment 'Calendar name',
    calendar             blob            not null            comment 'Serialized persistent Calendar object',
    primary key (sched_name, calendar_name)
) engine=innodb comment = 'Calendar information table';

-- ----------------------------
-- 7. Stores paused trigger group information
-- ---------------------------- 
create table QRTZ_PAUSED_TRIGGER_GRPS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    trigger_group        varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_group',
    primary key (sched_name, trigger_group)
) engine=innodb comment = 'Paused trigger group table';

-- ----------------------------
-- 8. Stores fired trigger state and associated job execution information
-- ---------------------------- 
create table QRTZ_FIRED_TRIGGERS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    entry_id             varchar(95)     not null            comment 'Scheduler instance entry ID',
    trigger_name         varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_name',
    trigger_group        varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_group',
    instance_name        varchar(200)    not null            comment 'Scheduler instance name',
    fired_time           bigint(13)      not null            comment 'Actual fire time',
    sched_time           bigint(13)      not null            comment 'Scheduled fire time',
    priority             integer         not null            comment 'Priority',
    state                varchar(16)     not null            comment 'State',
    job_name             varchar(200)    null                comment 'Job name',
    job_group            varchar(200)    null                comment 'Job group name',
    is_nonconcurrent     varchar(1)      null                comment 'Whether concurrent execution is disallowed',
    requests_recovery    varchar(1)      null                comment 'Whether recovery execution is requested',
    primary key (sched_name, entry_id)
) engine=innodb comment = 'Fired trigger table';

-- ----------------------------
-- 9. Stores scheduler state information used to track instances in a cluster
-- ---------------------------- 
create table QRTZ_SCHEDULER_STATE (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    instance_name        varchar(200)    not null            comment 'Instance name',
    last_checkin_time    bigint(13)      not null            comment 'Last check-in time',
    checkin_interval     bigint(13)      not null            comment 'Check-in interval',
    primary key (sched_name, instance_name)
) engine=innodb comment = 'Scheduler state table';

-- ----------------------------
-- 10. Stores pessimistic lock information when locking is enabled
-- ---------------------------- 
create table QRTZ_LOCKS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    lock_name            varchar(40)     not null            comment 'Lock name',
    primary key (sched_name, lock_name)
) engine=innodb comment = 'Scheduler lock table';

-- ----------------------------
-- 11. Stores extended trigger properties used by Quartz
-- ---------------------------- 
create table QRTZ_SIMPROP_TRIGGERS (
    sched_name           varchar(120)    not null            comment 'Scheduler name',
    trigger_name         varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_name',
    trigger_group        varchar(200)    not null            comment 'Foreign key to qrtz_triggers.trigger_group',
    str_prop_1           varchar(512)    null                comment 'First string trigger property',
    str_prop_2           varchar(512)    null                comment 'Second string trigger property',
    str_prop_3           varchar(512)    null                comment 'Third string trigger property',
    int_prop_1           int             null                comment 'First integer trigger property',
    int_prop_2           int             null                comment 'Second integer trigger property',
    long_prop_1          bigint          null                comment 'First long trigger property',
    long_prop_2          bigint          null                comment 'Second long trigger property',
    dec_prop_1           numeric(13,4)   null                comment 'First decimal trigger property',
    dec_prop_2           numeric(13,4)   null                comment 'Second decimal trigger property',
    bool_prop_1          varchar(1)      null                comment 'First Boolean trigger property',
    bool_prop_2          varchar(1)      null                comment 'Second Boolean trigger property',
    primary key (sched_name, trigger_name, trigger_group),
    foreign key (sched_name, trigger_name, trigger_group) references QRTZ_TRIGGERS(sched_name, trigger_name, trigger_group)
) engine=innodb comment = 'Simple property trigger table';

commit;
