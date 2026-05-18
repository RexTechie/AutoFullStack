package com.demo.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.demo.common.annotation.Excel;
import com.demo.common.annotation.Excel.ColumnType;
import com.demo.common.core.domain.BaseEntity;

/**
 * 操作日志记录表 oper_log
 * 
 */
public class SysOperLog extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 日志主键 */
    @Excel(name = "Operation Id", cellType = ColumnType.NUMERIC)
    private Long operId;

    /** 操作模块 */
    @Excel(name = "Operation Module")
    private String title;

    /** 业务类型（0其它 1新增 2修改 3删除） */
    @Excel(name = "Business Type", readConverterExp = "0=Other,1=Add,2=Edit,3=Delete,4=Authorization,5=Export,6=Import,7=ForceLogout,8=GenerateCode,9=Clear")
    private Integer businessType;

    /** 业务类型数组 */
    private Integer[] businessTypes;

    /** 请求方法 */
    @Excel(name = "Method")
    private String method;

    /** 请求方式 */
    @Excel(name = "Request Method")
    private String requestMethod;

    /** 操作类别（0其它 1后台用户 2手机端用户） */
    @Excel(name = "Operator Type", readConverterExp = "0=Other,1=Backend user,2=Mobile users")
    private Integer operatorType;

    /** 操作人员 */
    @Excel(name = "Operator")
    private String operName;

    /** 部门名称 */
    @Excel(name = "Department Name")
    private String deptName;

    /** 请求url */
    @Excel(name = "Request URL")
    private String operUrl;

    /** 操作地址 */
    @Excel(name = "IP")
    private String operIp;

    /** 操作地点 */
    @Excel(name = "Location")
    private String operLocation;

    /** 请求参数 */
    @Excel(name = "Operation Param")
    private String operParam;

    /** 返回参数 */
    @Excel(name = "Return Param")
    private String jsonResult;

    /** 操作状态（0正常 1异常） */
    @Excel(name = "Status", readConverterExp = "0=Normal,1=Abnormal")
    private Integer status;

    /** 错误消息 */
    @Excel(name = "Error Message")
    private String errorMsg;

    /** 操作时间 */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Excel(name = "Operation Time", width = 30, dateFormat = "yyyy-MM-dd HH:mm:ss")
    private Date operTime;

    /** 消耗时间 */
    @Excel(name = "Cost Time", suffix = "ms")
    private Long costTime;

    public Long getOperId()
    {
        return operId;
    }

    public void setOperId(Long operId)
    {
        this.operId = operId;
    }

    public String getTitle()
    {
        return title;
    }

    public void setTitle(String title)
    {
        this.title = title;
    }

    public Integer getBusinessType()
    {
        return businessType;
    }

    public void setBusinessType(Integer businessType)
    {
        this.businessType = businessType;
    }

    public Integer[] getBusinessTypes()
    {
        return businessTypes;
    }

    public void setBusinessTypes(Integer[] businessTypes)
    {
        this.businessTypes = businessTypes;
    }

    public String getMethod()
    {
        return method;
    }

    public void setMethod(String method)
    {
        this.method = method;
    }

    public String getRequestMethod()
    {
        return requestMethod;
    }

    public void setRequestMethod(String requestMethod)
    {
        this.requestMethod = requestMethod;
    }

    public Integer getOperatorType()
    {
        return operatorType;
    }

    public void setOperatorType(Integer operatorType)
    {
        this.operatorType = operatorType;
    }

    public String getOperName()
    {
        return operName;
    }

    public void setOperName(String operName)
    {
        this.operName = operName;
    }

    public String getDeptName()
    {
        return deptName;
    }

    public void setDeptName(String deptName)
    {
        this.deptName = deptName;
    }

    public String getOperUrl()
    {
        return operUrl;
    }

    public void setOperUrl(String operUrl)
    {
        this.operUrl = operUrl;
    }

    public String getOperIp()
    {
        return operIp;
    }

    public void setOperIp(String operIp)
    {
        this.operIp = operIp;
    }

    public String getOperLocation()
    {
        return operLocation;
    }

    public void setOperLocation(String operLocation)
    {
        this.operLocation = operLocation;
    }

    public String getOperParam()
    {
        return operParam;
    }

    public void setOperParam(String operParam)
    {
        this.operParam = operParam;
    }

    public String getJsonResult()
    {
        return jsonResult;
    }

    public void setJsonResult(String jsonResult)
    {
        this.jsonResult = jsonResult;
    }

    public Integer getStatus()
    {
        return status;
    }

    public void setStatus(Integer status)
    {
        this.status = status;
    }

    public String getErrorMsg()
    {
        return errorMsg;
    }

    public void setErrorMsg(String errorMsg)
    {
        this.errorMsg = errorMsg;
    }

    public Date getOperTime()
    {
        return operTime;
    }

    public void setOperTime(Date operTime)
    {
        this.operTime = operTime;
    }

    public Long getCostTime()
    {
        return costTime;
    }

    public void setCostTime(Long costTime)
    {
        this.costTime = costTime;
    }
}
