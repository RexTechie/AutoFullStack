<template>
  <div class="app-container">
     <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="User Name" prop="userName">
        <el-input
          v-model="queryParams.userName"
          placeholder="Please enter user name"
          clearable
          style="width: 240px"
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="Phone Number" prop="phonenumber">
        <el-input
          v-model="queryParams.phonenumber"
          placeholder="Please enter phone number"
          clearable
          style="width: 240px"
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">Search</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">Reset</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="openSelectUser"
          v-hasPermi="['system:role:add']"
        >Add User</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-circle-close"
          size="mini"
          :disabled="multiple"
          @click="cancelAuthUserAll"
          v-hasPermi="['system:role:remove']"
        >Batch Cancel Authorization</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-close"
          size="mini"
          @click="handleClose"
        >Close</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="userList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="User Name" prop="userName" :show-overflow-tooltip="true" />
      <el-table-column label="Nickname" prop="nickName" :show-overflow-tooltip="true" />
      <el-table-column label="Email" prop="email" :show-overflow-tooltip="true" />
      <el-table-column label="Phone" prop="phonenumber" :show-overflow-tooltip="true" />
      <el-table-column label="Status" align="center" prop="status">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.sys_normal_disable" :value="scope.row.status"/>
        </template>
      </el-table-column>
      <el-table-column label="Create Time" align="center" prop="createTime" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-circle-close"
            @click="cancelAuthUser(scope.row)"
            v-hasPermi="['system:role:remove']"
          >Cancel Authorization</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />
    <select-user ref="select" :roleId="queryParams.roleId" @ok="handleQuery" />
  </div>
</template>

<script>
import { allocatedUserList, authUserCancel, authUserCancelAll } from "@/api/system/role"
import selectUser from "./selectUser"

export default {
  name: "AuthUser",
  dicts: ['sys_normal_disable'],
  components: { selectUser },
  data() {
    return {
      // Loading mask
      loading: true,
      // Selected user group
      userIds: [],
      // Disable when not multiple
      multiple: true,
      // Show search conditions
      showSearch: true,
      // Total count
      total: 0,
      // User table data
      userList: [],
      // Query parameters
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        roleId: undefined,
        userName: undefined,
        phonenumber: undefined
      }
    }
  },
  created() {
    const roleId = this.$route.params && this.$route.params.roleId
    if (roleId) {
      this.queryParams.roleId = roleId
      this.getList()
    }
  },
  methods: {
    /** Query authorized user list */
    getList() {
      this.loading = true
      allocatedUserList(this.queryParams).then(response => {
          this.userList = response.rows
          this.total = response.total
          this.loading = false
        }
      )
    },
    // Back button
    handleClose() {
      const obj = { path: "/system/role" }
      this.$tab.closeOpenPage(obj)
    },
    /** Search button operation */
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    /** Reset button operation */
    resetQuery() {
      this.resetForm("queryForm")
      this.handleQuery()
    },
    // Multiple selection data
    handleSelectionChange(selection) {
      this.userIds = selection.map(item => item.userId)
      this.multiple = !selection.length
    },
    /** Open authorized user table popup */
    openSelectUser() {
      this.$refs.select.show()
    },
    /** Cancel authorization button operation */
    cancelAuthUser(row) {
      const roleId = this.queryParams.roleId
      this.$modal.confirm('Are you sure to cancel the role for user "' + row.userName + '"?').then(function() {
        return authUserCancel({ userId: row.userId, roleId: roleId })
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess("Authorization cancelled successfully")
      }).catch(() => {})
    },
    /** Batch cancel authorization button operation */
    cancelAuthUserAll(row) {
      const roleId = this.queryParams.roleId
      const userIds = this.userIds.join(",")
      this.$modal.confirm('Are you sure to cancel authorization for selected users?').then(function() {
        return authUserCancelAll({ roleId: roleId, userIds: userIds })
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess("Authorization cancelled successfully")
      }).catch(() => {})
    }
  }
}
</script>