<template>
  <div class="app-container">
    <h4 class="form-header h4">Basic Information</h4>
      <el-form ref="form" :model="form" label-width="150px">
      <el-row>
        <el-col :span="8" :offset="2">
          <el-form-item label="Nickname" prop="nickName">
            <el-input v-model="form.nickName" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8" :offset="2">
          <el-form-item label="Login Account" prop="userName">
            <el-input v-model="form.userName" disabled />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <h4 class="form-header h4">Role Information</h4>
    <el-table v-loading="loading" :row-key="getRowKey" @row-click="clickRow" ref="table" @selection-change="handleSelectionChange" :data="roles.slice((pageNum-1)*pageSize,pageNum*pageSize)">
      <el-table-column label="No." type="index" align="center">
        <template slot-scope="scope">
          <span>{{ (pageNum - 1) * pageSize + scope.$index + 1 }}</span>
        </template>
      </el-table-column>
      <el-table-column type="selection" :reserve-selection="true" :selectable="checkSelectable" width="55" />
      <el-table-column label="Role ID" align="center" prop="roleId" />
      <el-table-column label="Role Name" align="center" prop="roleName" />
      <el-table-column label="Permission Key" align="center" prop="roleKey" />
      <el-table-column label="Create Time" align="center" prop="createTime" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="pageNum" :limit.sync="pageSize" />

    <el-form label-width="150px">
      <el-form-item style="text-align: center;margin-left:-120px;margin-top:30px;">
        <el-button type="primary" @click="submitForm()">Submit</el-button>
        <el-button @click="close()">Back</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { getAuthRole, updateAuthRole } from "@/api/system/user"

export default {
  name: "AuthRole",
  data() {
    return {
      // Loading mask
      loading: true,
      // Pagination info
      total: 0,
      pageNum: 1,
      pageSize: 10,
      // Selected role IDs
      roleIds: [],
      // Role information
      roles: [],
      // User information
      form: {}
    }
  },
  created() {
    const userId = this.$route.params && this.$route.params.userId
    if (userId) {
      this.loading = true
      getAuthRole(userId).then((response) => {
        this.form = response.user
        this.roles = response.roles
        this.total = this.roles.length
        this.$nextTick(() => {
          this.roles.forEach((row) => {
            if (row.flag) {
              this.$refs.table.toggleRowSelection(row)
            }
          })
        })
        this.loading = false
      })
    }
  },
  methods: {
    /** Click to select row data */
    clickRow(row) {
      if (this.checkSelectable(row)) {
        this.$refs.table.toggleRowSelection(row)
      }
    },
    // Multiple selection data
    handleSelectionChange(selection) {
      this.roleIds = selection.map((item) => item.roleId)
    },
    // Save selected data ID
    getRowKey(row) {
      return row.roleId
    },
    // Check role status
    checkSelectable(row) {
      return row.status === "0" ? true : false
    },
    /** Submit button */
    submitForm() {
      const userId = this.form.userId
      const roleIds = this.roleIds.join(",")
      updateAuthRole({ userId: userId, roleIds: roleIds }).then((response) => {
        this.$modal.msgSuccess("Authorization successful")
        this.close()
      })
    },
    /** Close button */
    close() {
      const obj = { path: "/system/user" }
      this.$tab.closeOpenPage(obj)
    }
  }
}
</script>