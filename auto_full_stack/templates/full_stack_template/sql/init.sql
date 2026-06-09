-- ----------------------------
-- 1. Department table
-- ----------------------------
drop table if exists sys_dept;
create table sys_dept (
  dept_id           bigint(20)      not null auto_increment    comment 'Department ID',
  parent_id         bigint(20)      default 0                  comment 'Parent Department ID',
  ancestors         varchar(50)     default ''                 comment 'Ancestors List',
  dept_name         varchar(30)     default ''                 comment 'Department Name',
  order_num         int(4)          default 0                  comment 'Display Order',
  leader            varchar(20)     default null               comment 'Leader',
  phone             varchar(11)     default null               comment 'Phone Number',
  email             varchar(50)     default null               comment 'Email',
  status            char(1)         default '0'                comment 'Department Status (0 Normal 1 Disabled)',
  del_flag          char(1)         default '0'                comment 'Delete Flag (0 Exists 2 Deleted)',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time 	    datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  primary key (dept_id)
) engine=innodb auto_increment=200 comment = 'Department Table';

-- ----------------------------
-- Initialize department data
-- ----------------------------
insert into sys_dept values(100,  0,   '0',          'Software Development Company',   0, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(101,  100, '0,100',      'Shenzhen Headquarters', 1, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(102,  100, '0,100',      'Changsha Branch', 2, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(103,  101, '0,100,101',  'R&D Department',   1, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(104,  101, '0,100,101',  'Marketing Department',   2, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(105,  101, '0,100,101',  'Testing Department',   3, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(106,  101, '0,100,101',  'Finance Department',   4, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(107,  101, '0,100,101',  'Operations Department',   5, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(108,  102, '0,100,102',  'Marketing Department',   1, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);
insert into sys_dept values(109,  102, '0,100,102',  'Finance Department',   2, 'Administrator', '15888888888', 'admin@qq.com', '0', '0', 'admin', sysdate(), '', null);


-- ----------------------------
-- 2. User information table
-- ----------------------------
drop table if exists sys_user;
create table sys_user (
  user_id           bigint(20)      not null auto_increment    comment 'User ID',
  dept_id           bigint(20)      default null               comment 'Department ID',
  user_name         varchar(30)     not null                   comment 'User Account',
  nick_name         varchar(30)     not null                   comment 'User Nickname',
  user_type         varchar(2)      default '00'               comment 'User Type (00 System User)',
  email             varchar(50)     default ''                 comment 'User Email',
  phonenumber       varchar(11)     default ''                 comment 'Phone Number',
  sex               char(1)         default '0'                comment 'User Gender (0 Male 1 Female 2 Unknown)',
  avatar            varchar(100)    default ''                 comment 'Avatar URL',
  password          varchar(100)    default ''                 comment 'Password',
  status            char(1)         default '0'                comment 'Account Status (0 Normal 1 Disabled)',
  del_flag          char(1)         default '0'                comment 'Delete Flag (0 Exists 2 Deleted)',
  login_ip          varchar(128)    default ''                 comment 'Last Login IP',
  login_date        datetime                                   comment 'Last Login Time',
  pwd_update_date   datetime                                   comment 'Password Last Update Time',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time       datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  remark            varchar(500)    default null               comment 'Remark',
  primary key (user_id)
) engine=innodb auto_increment=100 comment = 'User Information Table';

-- ----------------------------
-- Initialize user information data
-- ----------------------------
insert into sys_user values(1,  100, 'admin', 'Administrator', '00', 'admin@163.com', '15888888888', '1', '', '$2a$10$ReSH1hWeztbuafGftr0afuOAME0X4Cr6mvoRB0hrj1ln8dBxh0VFS', '0', '0', '127.0.0.1', sysdate(), sysdate(), 'admin', sysdate(), '', null, 'Administrator');
insert into sys_user values(2,  105, 'tester',    'Tester', '00', 'tester@qq.com',  '15666666666', '1', '', '$2a$10$ReSH1hWeztbuafGftr0afuOAME0X4Cr6mvoRB0hrj1ln8dBxh0VFS', '0', '0', '127.0.0.1', sysdate(), sysdate(), 'admin', sysdate(), '', null, 'Tester');
insert into sys_user values(3,  103, 'developer',    'Developer', '00', 'developer@qq.com',  '15444444444', '1', '', '$2a$10$ReSH1hWeztbuafGftr0afuOAME0X4Cr6mvoRB0hrj1ln8dBxh0VFS', '0', '0', '127.0.0.1', sysdate(), sysdate(), 'admin', sysdate(), '', null, 'Developer');

-- ----------------------------
-- 3. Post information table
-- ----------------------------
drop table if exists sys_post;
create table sys_post
(
  post_id       bigint(20)      not null auto_increment    comment 'Post ID',
  post_code     varchar(64)     not null                   comment 'Post Code',
  post_name     varchar(50)     not null                   comment 'Post Name',
  post_sort     int(4)          not null                   comment 'Display Order',
  status        char(1)         not null                   comment 'Status (0 Normal 1 Disabled)',
  create_by     varchar(64)     default ''                 comment 'Created By',
  create_time   datetime                                   comment 'Create Time',
  update_by     varchar(64)     default ''			       comment 'Updated By',
  update_time   datetime                                   comment 'Update Time',
  remark        varchar(500)    default null               comment 'Remark',
  primary key (post_id)
) engine=innodb comment = 'Post Information Table';

-- ----------------------------
-- Initialize post information data
-- ----------------------------
insert into sys_post values(1, 'ceo',  'CEO',    1, '0', 'admin', sysdate(), '', null, '');
insert into sys_post values(2, 'se',   'Project Manager',  2, '0', 'admin', sysdate(), '', null, '');
insert into sys_post values(3, 'hr',   'Human Resources',  3, '0', 'admin', sysdate(), '', null, '');
insert into sys_post values(4, 'user', 'General Employee',  4, '0', 'admin', sysdate(), '', null, '');


-- ----------------------------
-- 4. Role information table
-- ----------------------------
drop table if exists sys_role;
create table sys_role (
  role_id              bigint(20)      not null auto_increment    comment 'Role ID',
  role_name            varchar(30)     not null                   comment 'Role Name',
  role_key             varchar(100)    not null                   comment 'Role Permission String',
  role_sort            int(4)          not null                   comment 'Display Order',
  data_scope           char(1)         default '1'                comment 'Data Scope (1: All Data Permission 2: Custom Data Permission 3: Department Data Permission 4: Department and Below Data Permission)',
  menu_check_strictly  tinyint(1)      default 1                  comment 'Whether Menu Tree Selection Items Are Associated Display',
  dept_check_strictly  tinyint(1)      default 1                  comment 'Whether Department Tree Selection Items Are Associated Display',
  status               char(1)         not null                   comment 'Role Status (0 Normal 1 Disabled)',
  del_flag             char(1)         default '0'                comment 'Delete Flag (0 Exists 2 Deleted)',
  create_by            varchar(64)     default ''                 comment 'Created By',
  create_time          datetime                                   comment 'Create Time',
  update_by            varchar(64)     default ''                 comment 'Updated By',
  update_time          datetime                                   comment 'Update Time',
  remark               varchar(500)    default null               comment 'Remark',
  primary key (role_id)
) engine=innodb auto_increment=100 comment = 'Role Information Table';

-- ----------------------------
-- Initialize role information data
-- ----------------------------
insert into sys_role values('1', 'Super Administrator',  'admin',  1, 1, 1, 1, '0', '0', 'admin', sysdate(), '', null, 'Super Administrator');
insert into sys_role values('2', 'Common Role',    'common', 2, 2, 1, 1, '0', '0', 'admin', sysdate(), '', null, 'Common Role');


-- ----------------------------
-- 5. Menu permission table
-- ----------------------------
drop table if exists sys_menu;
create table sys_menu (
  menu_id           bigint(20)      not null auto_increment    comment 'Menu ID',
  menu_name         varchar(50)     not null                   comment 'Menu Name',
  parent_id         bigint(20)      default 0                  comment 'Parent Menu ID',
  order_num         int(4)          default 0                  comment 'Display Order',
  path              varchar(200)    default ''                 comment 'Route Path',
  component         varchar(255)    default null               comment 'Component Path',
  query             varchar(255)    default null               comment 'Route Parameters',
  route_name        varchar(50)     default ''                 comment 'Route Name',
  is_frame          int(1)          default 1                  comment 'Is External Link (0 Yes 1 No)',
  is_cache          int(1)          default 0                  comment 'Is Cache (0 Cache 1 No Cache)',
  menu_type         char(1)         default ''                 comment 'Menu Type (M Directory C Menu F Button)',
  visible           char(1)         default 0                  comment 'Menu Status (0 Show 1 Hide)',
  status            char(1)         default 0                  comment 'Menu Status (0 Normal 1 Disabled)',
  perms             varchar(100)    default null               comment 'Permission Identifier',
  icon              varchar(100)    default '#'                comment 'Menu Icon',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time       datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  remark            varchar(500)    default ''                 comment 'Remark',
  primary key (menu_id)
) engine=innodb auto_increment=2000 comment = 'Menu Permission Table';

-- ----------------------------
-- Initialize menu information data
-- ----------------------------
-- Top-level menus
insert into sys_menu values('1', 'System', '0', '1', 'system',           null, '', '', 1, 0, 'M', '0', '0', '', 'system',   'admin', sysdate(), '', null, 'System Management Directory');
insert into sys_menu values('2', 'Monitor', '0', '2', 'monitor',          null, '', '', 1, 0, 'M', '0', '0', '', 'monitor',  'admin', sysdate(), '', null, 'System Monitor Directory');
insert into sys_menu values('3', 'Tools', '0', '3', 'tool',             null, '', '', 1, 0, 'M', '0', '0', '', 'tool',     'admin', sysdate(), '', null, 'System Tools Directory');
insert into sys_menu values('4', 'Business', '0', '0', 'business',             null, '', '', 1, 0, 'M', '0', '0', '', 'business',     'admin', sysdate(), '', null, 'Business Information Directory');
-- Second-level menus
insert into sys_menu values('100',  'SysUser', '1',   '1', 'user',       'system/user/index',        '', '', 1, 0, 'C', '0', '0', 'system:user:list',        'user',          'admin', sysdate(), '', null, 'SysUser management menu');
insert into sys_menu values('101',  'Role', '1',   '2', 'role',       'system/role/index',        '', '', 1, 0, 'C', '0', '0', 'system:role:list',        'peoples',       'admin', sysdate(), '', null, 'Role management menu');
insert into sys_menu values('102',  'Menu', '1',   '3', 'menu',       'system/menu/index',        '', '', 1, 0, 'C', '0', '0', 'system:menu:list',        'tree-table',    'admin', sysdate(), '', null, 'Menu management menu');
insert into sys_menu values('103',  'Department', '1',   '4', 'dept',       'system/dept/index',        '', '', 1, 0, 'C', '0', '0', 'system:dept:list',        'tree',          'admin', sysdate(), '', null, 'management Management menu');
insert into sys_menu values('104',  'Post', '1',   '5', 'post',       'system/post/index',        '', '', 1, 0, 'C', '0', '0', 'system:post:list',        'post',          'admin', sysdate(), '', null, 'Post management menu');
insert into sys_menu values('105',  'Dict', '1',   '6', 'dict',       'system/dict/index',        '', '', 1, 0, 'C', '0', '0', 'system:dict:list',        'dict',          'admin', sysdate(), '', null, 'Dictionary management menu');
insert into sys_menu values('106',  'Config', '1',   '7', 'config',     'system/config/index',      '', '', 1, 0, 'C', '0', '0', 'system:config:list',      'edit',          'admin', sysdate(), '', null, 'Parameter settings menu');
insert into sys_menu values('107',  'Notice', '1',   '8', 'notice',     'system/notice/index',      '', '', 1, 0, 'C', '0', '0', 'system:notice:list',      'message',       'admin', sysdate(), '', null, 'Notice management menu');
insert into sys_menu values('108',  'Log', '2',   '9', 'log',        '',                         '', '', 1, 0, 'M', '0', '0', '',                        'log',           'admin', sysdate(), '', null, 'Log management menu');
insert into sys_menu values('109',  'Online', '2',   '1', 'online',     'monitor/online/index',     '', '', 1, 0, 'C', '0', '0', 'monitor:online:list',     'online',        'admin', sysdate(), '', null, 'Online users menu');
insert into sys_menu values('110',  'Job', '2',   '2', 'job',        'monitor/job/index',        '', '', 1, 0, 'C', '0', '0', 'monitor:job:list',        'job',           'admin', sysdate(), '', null, 'Scheduled tasks menu');
insert into sys_menu values('111',  'Druid', '2',   '3', 'druid',      'monitor/druid/index',      '', '', 1, 0, 'C', '0', '0', 'monitor:druid:list',      'druid',         'admin', sysdate(), '', null, 'Data monitor menu');
insert into sys_menu values('112',  'Server', '2',   '4', 'server',     'monitor/server/index',     '', '', 1, 0, 'C', '0', '0', 'monitor:server:list',     'server',        'admin', sysdate(), '', null, 'Server monitor menu');
insert into sys_menu values('113',  'Cache', '2',   '5', 'cache',      'monitor/cache/index',      '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list',      'redis',         'admin', sysdate(), '', null, 'Cache monitor menu');
insert into sys_menu values('114',  'Cache List', '2',   '6', 'cacheList',  'monitor/cache/list',       '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list',      'redis-list',    'admin', sysdate(), '', null, 'Cache list menu');
insert into sys_menu values('115',  'Form Generator', '3',   '1', 'build',      'tool/build/index',         '', '', 1, 0, 'C', '0', '0', 'tool:build:list',         'build',         'admin', sysdate(), '', null, 'Form builder menu');
insert into sys_menu values('116',  'Code Generator', '3',   '2', 'gen',        'tool/gen/index',           '', '', 1, 0, 'C', '0', '0', 'tool:gen:list',           'code',          'admin', sysdate(), '', null, 'Code generator menu');
insert into sys_menu values('117',  'System API', '3',   '3', 'swagger',    'tool/swagger/index',       '', '', 1, 0, 'C', '0', '0', 'tool:swagger:list',       'swagger',       'admin', sysdate(), '', null, 'System API menu');
-- Third-level menus
insert into sys_menu values('500',  'Operation Log', '108', '1', 'operlog',    'monitor/operlog/index',    '', '', 1, 0, 'C', '0', '0', 'monitor:operlog:list',    'form',          'admin', sysdate(), '', null, 'Operation log menu');
insert into sys_menu values('501',  'Login Log', '108', '2', 'logininfor', 'monitor/logininfor/index', '', '', 1, 0, 'C', '0', '0', 'monitor:logininfor:list', 'logininfor',    'admin', sysdate(), '', null, 'Login log menu');
-- User management buttons
insert into sys_menu values('1000', 'SysUser Query', '100', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1001', 'SysUser Add', '100', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1002', 'SysUser Edit', '100', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1003', 'SysUser Delete', '100', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1004', 'SysUser Export', '100', '5',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:export',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1005', 'SysUser Import', '100', '6',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:import',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1006', 'Reset Password', '100', '7',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:resetPwd',       '#', 'admin', sysdate(), '', null, '');
-- Role management buttons
insert into sys_menu values('1007', 'Role Query', '101', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1008', 'Role Add', '101', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1009', 'Role Edit', '101', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1010', 'Role Delete', '101', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1011', 'Role Export', '101', '5',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:export',         '#', 'admin', sysdate(), '', null, '');
-- Menu management buttons
insert into sys_menu values('1012', 'Menu Query', '102', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1013', 'Menu Add', '102', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1014', 'Menu Edit', '102', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1015', 'Menu Delete', '102', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:remove',         '#', 'admin', sysdate(), '', null, '');
-- Department management buttons
insert into sys_menu values('1016', 'Department Query', '103', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1017', 'Department Add', '103', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1018', 'Department Edit', '103', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1019', 'Department Delete', '103', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:remove',         '#', 'admin', sysdate(), '', null, '');
-- Post management buttons
insert into sys_menu values('1020', 'Post Query', '104', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1021', 'Post Add', '104', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1022', 'Post Edit', '104', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1023', 'Post Delete', '104', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1024', 'Post Export', '104', '5',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:export',         '#', 'admin', sysdate(), '', null, '');
-- Dictionary management buttons
insert into sys_menu values('1025', 'Dict Query', '105', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1026', 'Dict Add', '105', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1027', 'Dict Edit', '105', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1028', 'Dict Delete', '105', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1029', 'Dict Export', '105', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:export',         '#', 'admin', sysdate(), '', null, '');
-- Parameter configuration buttons
insert into sys_menu values('1030', 'Config Query', '106', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:query',        '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1031', 'Config Add', '106', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:add',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1032', 'Config Edit', '106', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:edit',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1033', 'Config Delete', '106', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:remove',       '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1034', 'Config Export', '106', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:export',       '#', 'admin', sysdate(), '', null, '');
-- Notice management buttons
insert into sys_menu values('1035', 'Notice Query', '107', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:query',        '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1036', 'Notice Add', '107', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:add',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1037', 'Notice Edit', '107', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:edit',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1038', 'Notice Delete', '107', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:remove',       '#', 'admin', sysdate(), '', null, '');
-- Operation log buttons
insert into sys_menu values('1039', 'Operation Query', '500', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:query',      '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1040', 'Operation Delete', '500', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:remove',     '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1041', 'Log Export', '500', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:export',     '#', 'admin', sysdate(), '', null, '');
-- Login log buttons
insert into sys_menu values('1042', 'Login Query', '501', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:query',   '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1043', 'Login Delete', '501', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:remove',  '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1044', 'Log Export', '501', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:export',  '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1045', 'Account Unlock', '501', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:unlock',  '#', 'admin', sysdate(), '', null, '');
-- Online user buttons
insert into sys_menu values('1046', 'Online Query', '109', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:query',       '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1047', 'Batch Force Logout', '109', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:batchLogout', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1048', 'Single Force Logout', '109', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:forceLogout', '#', 'admin', sysdate(), '', null, '');
-- Scheduled task buttons
insert into sys_menu values('1049', 'Job Query', '110', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1050', 'Job Add', '110', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1051', 'Job Edit', '110', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1052', 'Job Delete', '110', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:remove',         '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1053', 'Status Change', '110', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:changeStatus',   '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1054', 'Task Export', '110', '6', '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:job:export',         '#', 'admin', sysdate(), '', null, '');
-- Code generation buttons
insert into sys_menu values('1055', 'Generate Query', '116', '1', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:query',             '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1056', 'Generate Edit', '116', '2', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:edit',              '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1057', 'Generate Delete', '116', '3', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:remove',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1058', 'Import Code', '116', '4', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:import',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1059', 'Preview Code', '116', '5', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:preview',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1060', 'Generate Code', '116', '6', '#', '', '', '', 1, 0, 'F', '0', '0', 'tool:gen:code',              '#', 'admin', sysdate(), '', null, '');


-- ----------------------------
-- 6. User-role association table: N-to-1 relationship
-- ----------------------------
drop table if exists sys_user_role;
create table sys_user_role (
  user_id   bigint(20) not null comment 'User ID',
  role_id   bigint(20) not null comment 'Role ID',
  primary key(user_id, role_id)
) engine=innodb comment = 'User and Role Association Table';

-- ----------------------------
-- Initialize user-role association data
-- ----------------------------
insert into sys_user_role values ('1', '1');
insert into sys_user_role values ('2', '2');


-- ----------------------------
-- 7. Role-menu association table: 1-to-N relationship
-- ----------------------------
drop table if exists sys_role_menu;
create table sys_role_menu (
  role_id   bigint(20) not null comment 'Role ID',
  menu_id   bigint(20) not null comment 'Menu ID',
  primary key(role_id, menu_id)
) engine=innodb comment = 'Role and Menu Association Table';

-- ----------------------------
-- Initialize role-menu association data
-- ----------------------------
insert into sys_role_menu values ('2', '1');
insert into sys_role_menu values ('2', '2');
insert into sys_role_menu values ('2', '3');
insert into sys_role_menu values ('2', '4');
insert into sys_role_menu values ('2', '100');
insert into sys_role_menu values ('2', '101');
insert into sys_role_menu values ('2', '102');
insert into sys_role_menu values ('2', '103');
insert into sys_role_menu values ('2', '104');
insert into sys_role_menu values ('2', '105');
insert into sys_role_menu values ('2', '106');
insert into sys_role_menu values ('2', '107');
insert into sys_role_menu values ('2', '108');
insert into sys_role_menu values ('2', '109');
insert into sys_role_menu values ('2', '110');
insert into sys_role_menu values ('2', '111');
insert into sys_role_menu values ('2', '112');
insert into sys_role_menu values ('2', '113');
insert into sys_role_menu values ('2', '114');
insert into sys_role_menu values ('2', '115');
insert into sys_role_menu values ('2', '116');
insert into sys_role_menu values ('2', '117');
insert into sys_role_menu values ('2', '500');
insert into sys_role_menu values ('2', '501');
insert into sys_role_menu values ('2', '1000');
insert into sys_role_menu values ('2', '1001');
insert into sys_role_menu values ('2', '1002');
insert into sys_role_menu values ('2', '1003');
insert into sys_role_menu values ('2', '1004');
insert into sys_role_menu values ('2', '1005');
insert into sys_role_menu values ('2', '1006');
insert into sys_role_menu values ('2', '1007');
insert into sys_role_menu values ('2', '1008');
insert into sys_role_menu values ('2', '1009');
insert into sys_role_menu values ('2', '1010');
insert into sys_role_menu values ('2', '1011');
insert into sys_role_menu values ('2', '1012');
insert into sys_role_menu values ('2', '1013');
insert into sys_role_menu values ('2', '1014');
insert into sys_role_menu values ('2', '1015');
insert into sys_role_menu values ('2', '1016');
insert into sys_role_menu values ('2', '1017');
insert into sys_role_menu values ('2', '1018');
insert into sys_role_menu values ('2', '1019');
insert into sys_role_menu values ('2', '1020');
insert into sys_role_menu values ('2', '1021');
insert into sys_role_menu values ('2', '1022');
insert into sys_role_menu values ('2', '1023');
insert into sys_role_menu values ('2', '1024');
insert into sys_role_menu values ('2', '1025');
insert into sys_role_menu values ('2', '1026');
insert into sys_role_menu values ('2', '1027');
insert into sys_role_menu values ('2', '1028');
insert into sys_role_menu values ('2', '1029');
insert into sys_role_menu values ('2', '1030');
insert into sys_role_menu values ('2', '1031');
insert into sys_role_menu values ('2', '1032');
insert into sys_role_menu values ('2', '1033');
insert into sys_role_menu values ('2', '1034');
insert into sys_role_menu values ('2', '1035');
insert into sys_role_menu values ('2', '1036');
insert into sys_role_menu values ('2', '1037');
insert into sys_role_menu values ('2', '1038');
insert into sys_role_menu values ('2', '1039');
insert into sys_role_menu values ('2', '1040');
insert into sys_role_menu values ('2', '1041');
insert into sys_role_menu values ('2', '1042');
insert into sys_role_menu values ('2', '1043');
insert into sys_role_menu values ('2', '1044');
insert into sys_role_menu values ('2', '1045');
insert into sys_role_menu values ('2', '1046');
insert into sys_role_menu values ('2', '1047');
insert into sys_role_menu values ('2', '1048');
insert into sys_role_menu values ('2', '1049');
insert into sys_role_menu values ('2', '1050');
insert into sys_role_menu values ('2', '1051');
insert into sys_role_menu values ('2', '1052');
insert into sys_role_menu values ('2', '1053');
insert into sys_role_menu values ('2', '1054');
insert into sys_role_menu values ('2', '1055');
insert into sys_role_menu values ('2', '1056');
insert into sys_role_menu values ('2', '1057');
insert into sys_role_menu values ('2', '1058');
insert into sys_role_menu values ('2', '1059');
insert into sys_role_menu values ('2', '1060');

-- ----------------------------
-- 8. Role-department association table: 1-to-N relationship
-- ----------------------------
drop table if exists sys_role_dept;
create table sys_role_dept (
  role_id   bigint(20) not null comment 'Role ID',
  dept_id   bigint(20) not null comment 'Department ID',
  primary key(role_id, dept_id)
) engine=innodb comment = 'Role and Department Association Table';

-- ----------------------------
-- Initialize role-department association data
-- ----------------------------
insert into sys_role_dept values ('2', '100');
insert into sys_role_dept values ('2', '101');
insert into sys_role_dept values ('2', '105');


-- ----------------------------
-- 9. User-post association table: 1-to-N relationship
-- ----------------------------
drop table if exists sys_user_post;
create table sys_user_post
(
  user_id   bigint(20) not null comment 'User ID',
  post_id   bigint(20) not null comment 'Post ID',
  primary key (user_id, post_id)
) engine=innodb comment = 'User and Post Association Table';

-- ----------------------------
-- Initialize user-post association data
-- ----------------------------
insert into sys_user_post values ('1', '1');
insert into sys_user_post values ('2', '2');


-- ----------------------------
-- 10. Operation log records
-- ----------------------------
drop table if exists sys_oper_log;
create table sys_oper_log (
  oper_id           bigint(20)      not null auto_increment    comment 'Log Primary Key',
  title             varchar(50)     default ''                 comment 'Module Title',
  business_type     int(2)          default 0                  comment 'Business Type (0 Other 1 Add 2 Edit 3 Delete)',
  method            varchar(200)    default ''                 comment 'Method Name',
  request_method    varchar(10)     default ''                 comment 'Request Method',
  operator_type     int(1)          default 0                  comment 'Operator Type (0 Other 1 Backend User 2 Mobile User)',
  oper_name         varchar(50)     default ''                 comment 'Operator Name',
  dept_name         varchar(50)     default ''                 comment 'Department Name',
  oper_url          varchar(255)    default ''                 comment 'Request URL',
  oper_ip           varchar(128)    default ''                 comment 'Host Address',
  oper_location     varchar(255)    default ''                 comment 'Operation Location',
  oper_param        varchar(2000)   default ''                 comment 'Request Parameters',
  json_result       varchar(2000)   default ''                 comment 'Response Parameters',
  status            int(1)          default 0                  comment 'Operation Status (0 Normal 1 Exception)',
  error_msg         varchar(2000)   default ''                 comment 'Error Message',
  oper_time         datetime                                   comment 'Operation Time',
  cost_time         bigint(20)      default 0                  comment 'Cost Time',
  primary key (oper_id),
  key idx_sys_oper_log_bt (business_type),
  key idx_sys_oper_log_s  (status),
  key idx_sys_oper_log_ot (oper_time)
) engine=innodb auto_increment=100 comment = 'Operation Log Record';


-- ----------------------------
-- 11. Dictionary type table
-- ----------------------------
drop table if exists sys_dict_type;
create table sys_dict_type
(
  dict_id          bigint(20)      not null auto_increment    comment 'Dictionary Primary Key',
  dict_name        varchar(100)    default ''                 comment 'Dictionary Name',
  dict_type        varchar(100)    default ''                 comment 'Dictionary Type',
  status           char(1)         default '0'                comment 'Status (0 Normal 1 Disabled)',
  create_by        varchar(64)     default ''                 comment 'Created By',
  create_time      datetime                                   comment 'Create Time',
  update_by        varchar(64)     default ''                 comment 'Updated By',
  update_time      datetime                                   comment 'Update Time',
  remark           varchar(500)    default null               comment 'Remark',
  primary key (dict_id),
  unique (dict_type)
) engine=innodb auto_increment=100 comment = 'Dictionary Type Table';

insert into sys_dict_type values(1,  'User Gender', 'sys_user_sex',        '0', 'admin', sysdate(), '', null, 'User Gender List');
insert into sys_dict_type values(2,  'Menu Status', 'sys_show_hide',       '0', 'admin', sysdate(), '', null, 'Menu Status List');
insert into sys_dict_type values(3,  'System Switch', 'sys_normal_disable',  '0', 'admin', sysdate(), '', null, 'System Switch List');
insert into sys_dict_type values(4,  'Task Status', 'sys_job_status',      '0', 'admin', sysdate(), '', null, 'Task Status List');
insert into sys_dict_type values(5,  'Task Group', 'sys_job_group',       '0', 'admin', sysdate(), '', null, 'Task Group List');
insert into sys_dict_type values(6,  'System Yes No', 'sys_yes_no',          '0', 'admin', sysdate(), '', null, 'System Yes No List');
insert into sys_dict_type values(7,  'Notice Type', 'sys_notice_type',     '0', 'admin', sysdate(), '', null, 'Notice Type List');
insert into sys_dict_type values(8,  'Notice Status', 'sys_notice_status',   '0', 'admin', sysdate(), '', null, 'Notice Status List');
insert into sys_dict_type values(9,  'Operation Type', 'sys_oper_type',       '0', 'admin', sysdate(), '', null, 'Operation Type List');
insert into sys_dict_type values(10, 'System Status', 'sys_common_status',   '0', 'admin', sysdate(), '', null, 'Login Status List');


-- ----------------------------
-- 12. Dictionary data table
-- ----------------------------
drop table if exists sys_dict_data;
create table sys_dict_data
(
  dict_code        bigint(20)      not null auto_increment    comment 'Dictionary Code',
  dict_sort        int(4)          default 0                  comment 'Dictionary Sort',
  dict_label       varchar(100)    default ''                 comment 'Dictionary Label',
  dict_value       varchar(100)    default ''                 comment 'Dictionary Value',
  dict_type        varchar(100)    default ''                 comment 'Dictionary Type',
  css_class        varchar(100)    default null               comment 'CSS Class (Other Style Extensions)',
  list_class       varchar(100)    default null               comment 'List Display Style',
  is_default       char(1)         default 'N'                comment 'Is Default (Y Yes N No)',
  status           char(1)         default '0'                comment 'Status (0 Normal 1 Disabled)',
  create_by        varchar(64)     default ''                 comment 'Created By',
  create_time      datetime                                   comment 'Create Time',
  update_by        varchar(64)     default ''                 comment 'Updated By',
  update_time      datetime                                   comment 'Update Time',
  remark           varchar(500)    default null               comment 'Remark',
  primary key (dict_code)
) engine=innodb auto_increment=100 comment = 'Dictionary Data Table';

insert into sys_dict_data values(1,  1,  'Male',       '0',       'sys_user_sex',        '',   '',        'Y', '0', 'admin', sysdate(), '', null, 'Male Gender');
insert into sys_dict_data values(2,  2,  'Female',       '1',       'sys_user_sex',        '',   '',        'N', '0', 'admin', sysdate(), '', null, 'Female Gender');
insert into sys_dict_data values(3,  3,  'Unknown',     '2',       'sys_user_sex',        '',   '',        'N', '0', 'admin', sysdate(), '', null, 'Unknown Gender');
insert into sys_dict_data values(4,  1,  'Show',     '0',       'sys_show_hide',       '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, 'Show Menu');
insert into sys_dict_data values(5,  2,  'Hide',     '1',       'sys_show_hide',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Hide Menu');
insert into sys_dict_data values(6,  1,  'Normal',     '0',       'sys_normal_disable',  '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, 'Normal Status');
insert into sys_dict_data values(7,  2,  'Disabled',     '1',       'sys_normal_disable',  '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Disabled Status');
insert into sys_dict_data values(8,  1,  'Normal',     '0',       'sys_job_status',      '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, 'Normal Status');
insert into sys_dict_data values(9,  2,  'Pause',     '1',       'sys_job_status',      '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Pause Status');
insert into sys_dict_data values(10, 1,  'Default',     'DEFAULT', 'sys_job_group',       '',   '',        'Y', '0', 'admin', sysdate(), '', null, 'Default Group');
insert into sys_dict_data values(11, 2,  'System',     'SYSTEM',  'sys_job_group',       '',   '',        'N', '0', 'admin', sysdate(), '', null, 'System Group');
insert into sys_dict_data values(12, 1,  'Yes',       'Y',       'sys_yes_no',          '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, 'System Default Yes');
insert into sys_dict_data values(13, 2,  'No',       'N',       'sys_yes_no',          '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'System Default No');
insert into sys_dict_data values(14, 1,  'Notice',     '1',       'sys_notice_type',     '',   'warning', 'Y', '0', 'admin', sysdate(), '', null, 'Notice');
insert into sys_dict_data values(15, 2,  'Announcement',     '2',       'sys_notice_type',     '',   'success', 'N', '0', 'admin', sysdate(), '', null, 'Announcement');
insert into sys_dict_data values(16, 1,  'Normal',     '0',       'sys_notice_status',   '',   'primary', 'Y', '0', 'admin', sysdate(), '', null, 'Normal Status');
insert into sys_dict_data values(17, 2,  'Closed',     '1',       'sys_notice_status',   '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Closed Status');
insert into sys_dict_data values(18, 99, 'Other',     '0',       'sys_oper_type',       '',   'info',    'N', '0', 'admin', sysdate(), '', null, 'Other Operation');
insert into sys_dict_data values(19, 1,  'Add',     '1',       'sys_oper_type',       '',   'info',    'N', '0', 'admin', sysdate(), '', null, 'Add Operation');
insert into sys_dict_data values(20, 2,  'Edit',     '2',       'sys_oper_type',       '',   'info',    'N', '0', 'admin', sysdate(), '', null, 'Edit Operation');
insert into sys_dict_data values(21, 3,  'Delete',     '3',       'sys_oper_type',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Delete Operation');
insert into sys_dict_data values(22, 4,  'Authorize',     '4',       'sys_oper_type',       '',   'primary', 'N', '0', 'admin', sysdate(), '', null, 'Authorize Operation');
insert into sys_dict_data values(23, 5,  'Export',     '5',       'sys_oper_type',       '',   'warning', 'N', '0', 'admin', sysdate(), '', null, 'Export Operation');
insert into sys_dict_data values(24, 6,  'Import',     '6',       'sys_oper_type',       '',   'warning', 'N', '0', 'admin', sysdate(), '', null, 'Import Operation');
insert into sys_dict_data values(25, 7,  'Force Logout',     '7',       'sys_oper_type',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Force Logout Operation');
insert into sys_dict_data values(26, 8,  'Generate Code', '8',       'sys_oper_type',       '',   'warning', 'N', '0', 'admin', sysdate(), '', null, 'Generate Operation');
insert into sys_dict_data values(27, 9,  'Clear Data', '9',       'sys_oper_type',       '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Clear Operation');
insert into sys_dict_data values(28, 1,  'Success',     '0',       'sys_common_status',   '',   'primary', 'N', '0', 'admin', sysdate(), '', null, 'Success Status');
insert into sys_dict_data values(29, 2,  'Failed',     '1',       'sys_common_status',   '',   'danger',  'N', '0', 'admin', sysdate(), '', null, 'Failed Status');


-- ----------------------------
-- 13. Parameter configuration table
-- ----------------------------
drop table if exists sys_config;
create table sys_config (
  config_id         int(5)          not null auto_increment    comment 'Parameter Primary Key',
  config_name       varchar(100)    default ''                 comment 'Parameter Name',
  config_key        varchar(100)    default ''                 comment 'Parameter Key',
  config_value      varchar(500)    default ''                 comment 'Parameter Value',
  config_type       char(1)         default 'N'                comment 'System Built-in (Y Yes N No)',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time       datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  remark            varchar(500)    default null               comment 'Remark',
  primary key (config_id)
) engine=innodb auto_increment=100 comment = 'Parameter Configuration Table';

insert into sys_config values(1, 'Main Framework Page-Default Skin Style Name',     'sys.index.skinName',               'skin-blue',     'Y', 'admin', sysdate(), '', null, 'Blue skin-blue, Green skin-green, Purple skin-purple, Red skin-red, Yellow skin-yellow' );
insert into sys_config values(2, 'User Management-Account Initial Password',         'sys.user.initPassword',            '88888888',        'Y', 'admin', sysdate(), '', null, 'Initial password 123456' );
insert into sys_config values(3, 'Main Framework Page-Sidebar Theme',           'sys.index.sideTheme',              'theme-dark',    'Y', 'admin', sysdate(), '', null, 'Dark theme theme-dark, Light theme theme-light' );
insert into sys_config values(4, 'Account Self-Service-Captcha Switch',           'sys.account.captchaEnabled',       'true',          'Y', 'admin', sysdate(), '', null, 'Whether to enable captcha function (true enable, false disable)');
insert into sys_config values(5, 'Account Self-Service-User Registration Function', 'sys.account.registerUser',         'false',         'Y', 'admin', sysdate(), '', null, 'Whether to enable user registration function (true enable, false disable)');
insert into sys_config values(6, 'User Login-Blacklist List',           'sys.login.blackIPList',            '',              'Y', 'admin', sysdate(), '', null, 'Set login IP blacklist restrictions, multiple matches separated by semicolons, support matching (* wildcard, network segment)');
insert into sys_config values(7, 'User Management-Initial Password Modification Strategy',     'sys.account.initPasswordModify',   '1',             'Y', 'admin', sysdate(), '', null, '0: Initial password modification strategy is closed, no prompt, 1: Remind user, if initial password is not modified, login will remind password modification dialog');
insert into sys_config values(8, 'User Management-Account Password Update Cycle',     'sys.account.passwordValidateDays', '0',             'Y', 'admin', sysdate(), '', null, 'Password update cycle (fill in number, data initialization value is 0 unlimited, if modified must be positive integer greater than 0 and less than 365), if this cycle is exceeded when logging in, login will remind password modification dialog');


-- ----------------------------
-- 14. System access records
-- ----------------------------
drop table if exists sys_logininfor;
create table sys_logininfor (
  info_id        bigint(20)     not null auto_increment   comment 'Access ID',
  user_name      varchar(50)    default ''                comment 'User Account',
  ipaddr         varchar(128)   default ''                comment 'Login IP Address',
  login_location varchar(255)   default ''                comment 'Login Location',
  browser        varchar(50)    default ''                comment 'Browser Type',
  os             varchar(50)    default ''                comment 'Operating System',
  status         char(1)        default '0'               comment 'Login Status (0 Success 1 Failed)',
  msg            varchar(255)   default ''                comment 'Message',
  login_time     datetime                                 comment 'Access Time',
  primary key (info_id),
  key idx_sys_logininfor_s  (status),
  key idx_sys_logininfor_lt (login_time)
) engine=innodb auto_increment=100 comment = 'System Access Record';


-- ----------------------------
-- 15. Scheduled task table
-- ----------------------------
drop table if exists sys_job;
create table sys_job (
  job_id              bigint(20)    not null auto_increment    comment 'Job ID',
  job_name            varchar(64)   default ''                 comment 'Job Name',
  job_group           varchar(64)   default 'DEFAULT'          comment 'Job Group',
  invoke_target       varchar(500)  not null                   comment 'Invoke Target String',
  cron_expression     varchar(255)  default ''                 comment 'Cron Expression',
  misfire_policy      varchar(20)   default '3'                comment 'Misfire Policy (1 Execute Immediately 2 Execute Once 3 Abandon Execution)',
  concurrent          char(1)       default '1'                comment 'Concurrent Execution (0 Allow 1 Forbid)',
  status              char(1)       default '0'                comment 'Status (0 Normal 1 Pause)',
  create_by           varchar(64)   default ''                 comment 'Created By',
  create_time         datetime                                 comment 'Create Time',
  update_by           varchar(64)   default ''                 comment 'Updated By',
  update_time         datetime                                 comment 'Update Time',
  remark              varchar(500)  default ''                 comment 'Remark',
  primary key (job_id, job_name, job_group)
) engine=innodb auto_increment=100 comment = 'Scheduled Task Dispatch Table';

insert into sys_job values(1, 'System Default (No Parameters)', 'DEFAULT', 'ryTask.ryNoParams',        '0/10 * * * * ?', '3', '1', '1', 'admin', sysdate(), '', null, '');
insert into sys_job values(2, 'System Default (With Parameters)', 'DEFAULT', 'ryTask.ryParams(\'ry\')',  '0/15 * * * * ?', '3', '1', '1', 'admin', sysdate(), '', null, '');
insert into sys_job values(3, 'System Default (Multiple Parameters)', 'DEFAULT', 'ryTask.ryMultipleParams(\'ry\', true, 2000L, 316.50D, 100)',  '0/20 * * * * ?', '3', '1', '1', 'admin', sysdate(), '', null, '');


-- ----------------------------
-- 16. Scheduled task log table
-- ----------------------------
drop table if exists sys_job_log;
create table sys_job_log (
  job_log_id          bigint(20)     not null auto_increment    comment 'Job Log ID',
  job_name            varchar(64)    not null                   comment 'Job Name',
  job_group           varchar(64)    not null                   comment 'Job Group',
  invoke_target       varchar(500)   not null                   comment 'Invoke Target String',
  job_message         varchar(500)                              comment 'Log Information',
  status              char(1)        default '0'                comment 'Execution Status (0 Normal 1 Failed)',
  exception_info      varchar(2000)  default ''                 comment 'Exception Information',
  create_time         datetime                                  comment 'Create Time',
  primary key (job_log_id)
) engine=innodb comment = 'Scheduled Task Dispatch Log Table';


-- ----------------------------
-- 17. Notice table
-- ----------------------------
drop table if exists sys_notice;
create table sys_notice (
  notice_id         int(4)          not null auto_increment    comment 'Notice ID',
  notice_title      varchar(100)     not null                   comment 'Notice Title',
  notice_type       char(1)         not null                   comment 'Notice Type (1 Notice 2 Announcement)',
  notice_content    longblob        default null               comment 'Notice Content',
  status            char(1)         default '0'                comment 'Notice Status (0 Normal 1 Closed)',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time       datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  remark            varchar(255)    default null               comment 'Remark',
  primary key (notice_id)
) engine=innodb auto_increment=10 comment = 'Notice Announcement Table';

-- ----------------------------
-- Initialize notice information data
-- ----------------------------
insert into sys_notice values('1', 'Warm Reminder: 2018-07-01 New Version Released', '2', 'New Version Content', '0', 'admin', sysdate(), '', null, 'Administrator');
insert into sys_notice values('2', 'Maintenance Notice: 2018-07-01 System Maintenance at Dawn', '1', 'Maintenance Content',   '0', 'admin', sysdate(), '', null, 'Administrator');


-- ----------------------------
-- 18. Code generation business table
-- ----------------------------
drop table if exists gen_table;
create table gen_table (
  table_id          bigint(20)      not null auto_increment    comment 'Table ID',
  table_name        varchar(200)    default ''                 comment 'Table Name',
  table_comment     varchar(500)    default ''                 comment 'Table Description',
  sub_table_name    varchar(64)     default null               comment 'Sub Table Name',
  sub_table_fk_name varchar(64)     default null               comment 'Sub Table Foreign Key Name',
  class_name        varchar(100)    default ''                 comment 'Entity Class Name',
  tpl_category      varchar(200)    default 'crud'             comment 'Template Category (crud single table operation tree tree table operation)',
  tpl_web_type      varchar(30)     default ''                 comment 'Frontend Template Type (element-ui template element-plus template)',
  package_name      varchar(100)                               comment 'Generated Package Path',
  module_name       varchar(30)                                comment 'Generated Module Name',
  business_name     varchar(30)                                comment 'Generated Business Name',
  function_name     varchar(50)                                comment 'Generated Function Name',
  function_author   varchar(50)                                comment 'Generated Function Author',
  gen_type          char(1)         default '0'                comment 'Code Generation Method (0 zip package 1 custom path)',
  gen_path          varchar(200)    default '/'                comment 'Generation Path (default project path if not filled)',
  options           varchar(1000)                              comment 'Other Generation Options',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time 	    datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  remark            varchar(500)    default null               comment 'Remark',
  primary key (table_id)
) engine=innodb auto_increment=1 comment = 'Code Generation Business Table';


-- ----------------------------
-- 19. Code generation business table columns
-- ----------------------------
drop table if exists gen_table_column;
create table gen_table_column (
  column_id         bigint(20)      not null auto_increment    comment 'Column ID',
  table_id          bigint(20)                                 comment 'Belonging Table ID',
  column_name       varchar(200)                               comment 'Column Name',
  column_comment    varchar(500)                               comment 'Column Description',
  column_type       varchar(100)                               comment 'Column Type',
  java_type         varchar(500)                               comment 'Java Type',
  java_field        varchar(200)                               comment 'Java Field Name',
  is_pk             char(1)                                    comment 'Is Primary Key (1 Yes)',
  is_increment      char(1)                                    comment 'Is Auto Increment (1 Yes)',
  is_required       char(1)                                    comment 'Is Required (1 Yes)',
  is_insert         char(1)                                    comment 'Is Insert Field (1 Yes)',
  is_edit           char(1)                                    comment 'Is Edit Field (1 Yes)',
  is_list           char(1)                                    comment 'Is List Field (1 Yes)',
  is_query          char(1)                                    comment 'Is Query Field (1 Yes)',
  query_type        varchar(200)    default 'EQ'               comment 'Query Method (Equal, Not Equal, Greater Than, Less Than, Range)',
  html_type         varchar(200)                               comment 'Display Type (Text Box, Text Area, Dropdown, Checkbox, Radio Button, Date Control)',
  dict_type         varchar(200)    default ''                 comment 'Dictionary Type',
  sort              int                                        comment 'Sort',
  create_by         varchar(64)     default ''                 comment 'Created By',
  create_time 	    datetime                                   comment 'Create Time',
  update_by         varchar(64)     default ''                 comment 'Updated By',
  update_time       datetime                                   comment 'Update Time',
  primary key (column_id)
) engine=innodb auto_increment=1 comment = 'Code Generation Business Table Column';
