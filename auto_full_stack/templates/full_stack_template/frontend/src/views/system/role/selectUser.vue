<template>
  <!-- Authorize User -->
  <el-dialog title="Select User" :visible.sync="visible" width="800px" top="5vh" append-to-body>
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true">
      <el-form-item label="User Name" prop="userName">
        <el-input
          v-model="queryParams.userName"
          placeholder="Please enter user name"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="Phone Number" prop="phonenumber">
        <el-input
          v-model="queryParams.phonenumber"
          placeholder="Please enter phone number"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">Search</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">Reset</el-button>
      </el-form-item>
    </el-form>
    <el-row>
      <el-table @row-click="clickRow" ref="table" :data="userList" @selection-change="handleSelectionChange" height="260px">
        <el-table-column type="selection" width="55"></el-table-column>
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
      </el-table>
      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="getList"
      />
    </el-row>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="handleSelectUser">Confirm</el-button>
      <el-button @click="visible = false">Cancel</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { unallocatedUserList, authUserSelectAll } from "@/api/system/role"
export default {
  dicts: ['sys_normal_disable'],
  props: {
    // Role ID
    roleId: {
      type: [Number, String]
    }
  },
  data() {
    return {
      // Loading mask
      visible: false,
      // Selected array values
      userIds: [],
      // Total count
      total: 0,
      // Unauthorized user data
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
  methods: {
    // Show popup
    show() {
      this.queryParams.roleId = this.roleId
      this.getList()
      this.visible = true
    },
    clickRow(row) {
      this.$refs.table.toggleRowSelection(row)
    },
    // Multiple selection data
    handleSelectionChange(selection) {
      this.userIds = selection.map(item => item.userId)
    },
    // Query table data
    getList() {
      unallocatedUserList(this.queryParams).then(res => {
        this.userList = res.rows
        this.total = res.total
      })
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
    /** Select authorized user operation */
    handleSelectUser() {
      const roleId = this.queryParams.roleId
      const userIds = this.userIds.join(",")
      if (userIds == "") {
        this.$modal.msgError("Please select users to assign")
        return
      }
      authUserSelectAll({ roleId: roleId, userIds: userIds }).then(res => {
        this.$modal.msgSuccess(res.msg)
        this.visible = false
        this.$emit("ok")
      })
    }
  }
}
</script>
