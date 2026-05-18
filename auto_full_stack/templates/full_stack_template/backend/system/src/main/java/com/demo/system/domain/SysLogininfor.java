package com.demo.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.demo.common.annotation.Excel;
import com.demo.common.annotation.Excel.ColumnType;
import com.demo.common.core.domain.BaseEntity;

/**
 * 系统访问记录表 sys_logininfor
 * 
 */
public class SysLogininfor extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** ID */
    @Excel(name = "ID", cellType = ColumnType.NUMERIC)
    private Long infoId;

    /** 用户账号 */
    @Excel(name = "User Name")
    private String userName;

    /** 登录状态 0成功 1失败 */
    @Excel(name = "Status", readConverterExp = "0=Success,1=Failure")
    private String status;

    /** 登录IP地址 */
    @Excel(name = "IP")
    private String ipaddr;

    /** 登录地点 */
    @Excel(name = "Location")
    private String loginLocation;

    /** 浏览器类型 */
    @Excel(name = "Browser")
    private String browser;

    /** 操作系统 */
    @Excel(name = "OS")
    private String os;

    /** 提示消息 */
    @Excel(name = "Message")
    private String msg;

    /** 访问时间 */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Excel(name = "Login Time", width = 30, dateFormat = "yyyy-MM-dd HH:mm:ss")
    private Date loginTime;

    public Long getInfoId()
    {
        return infoId;
    }

    public void setInfoId(Long infoId)
    {
        this.infoId = infoId;
    }

    public String getUserName()
    {
        return userName;
    }

    public void setUserName(String userName)
    {
        this.userName = userName;
    }

    public String getStatus()
    {
        return status;
    }

    public void setStatus(String status)
    {
        this.status = status;
    }

    public String getIpaddr()
    {
        return ipaddr;
    }

    public void setIpaddr(String ipaddr)
    {
        this.ipaddr = ipaddr;
    }

    public String getLoginLocation()
    {
        return loginLocation;
    }

    public void setLoginLocation(String loginLocation)
    {
        this.loginLocation = loginLocation;
    }

    public String getBrowser()
    {
        return browser;
    }

    public void setBrowser(String browser)
    {
        this.browser = browser;
    }

    public String getOs()
    {
        return os;
    }

    public void setOs(String os)
    {
        this.os = os;
    }

    public String getMsg()
    {
        return msg;
    }

    public void setMsg(String msg)
    {
        this.msg = msg;
    }

    public Date getLoginTime()
    {
        return loginTime;
    }

    public void setLoginTime(Date loginTime)
    {
        this.loginTime = loginTime;
    }
}
