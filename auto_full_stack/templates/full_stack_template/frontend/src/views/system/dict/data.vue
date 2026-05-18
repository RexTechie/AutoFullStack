<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="Dict Name" prop="dictType">
        <el-select v-model="queryParams.dictType">
          <el-option
            v-for="item in typeOptions"
            :key="item.dictId"
            :label="item.dictName"
            :value="item.dictType"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="Dict Label" prop="dictLabel">
        <el-input
          v-model="queryParams.dictLabel"
          placeholder="Please enter Dict label"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="Status" prop="status">
        <el-select v-model="queryParams.status" placeholder="Data Status" clearable>
          <el-option
            v-for="dict in dict.type.sys_normal_disable"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
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
          @click="handleAdd"
          v-hasPermi="['system:dict:add']"
        >Add</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="el-icon-edit"
          size="mini"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['system:dict:edit']"
        >Edit</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['system:dict:remove']"
        >Delete</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
          v-hasPermi="['system:dict:export']"
        >Export</el-button>
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

    <el-table v-loading="loading" :data="dataList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="Dict Code" align="center" prop="dictCode" />
      <el-table-column label="Dict Label" align="center" prop="dictLabel">
        <template slot-scope="scope">
          <span v-if="(scope.row.listClass == '' || scope.row.listClass == 'default') && (scope.row.cssClass == '' || scope.row.cssClass == null)">{{ scope.row.dictLabel }}</span>
          <el-tag v-else :type="scope.row.listClass == 'primary' ? '' : scope.row.listClass" :class="scope.row.cssClass">{{ scope.row.dictLabel }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Dict Value" align="center" prop="dictValue" />
      <el-table-column label="Dict Sort" align="center" prop="dictSort" />
      <el-table-column label="Status" align="center" prop="status">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.sys_normal_disable" :value="scope.row.status"/>
        </template>
      </el-table-column>
      <el-table-column label="Remark" align="center" prop="remark" :show-overflow-tooltip="true" />
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
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['system:dict:edit']"
          >Edit</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['system:dict:remove']"
          >Delete</el-button>
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

    <!-- Add or Edit Dict Data Dialog -->
    <el-dialog :title="title" :visible.sync="open" width="800px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="150px">
        <el-form-item label="Dict Type">
          <el-input v-model="form.dictType" :disabled="true" />
        </el-form-item>
        <el-form-item label="Data Label" prop="dictLabel">
          <el-input v-model="form.dictLabel" placeholder="Please enter data label" />
        </el-form-item>
        <el-form-item label="Data Value" prop="dictValue">
          <el-input v-model="form.dictValue" placeholder="Please enter data value" />
        </el-form-item>
        <el-form-item label="CSS Class" prop="cssClass">
          <el-input v-model="form.cssClass" placeholder="Please enter CSS class" />
        </el-form-item>
        <el-form-item label="Display Sort" prop="dictSort">
          <el-input-number v-model="form.dictSort" controls-position="right" :min="0" />
        </el-form-item>
        <el-form-item label="List Style" prop="listClass">
          <el-select v-model="form.listClass">
            <el-option
              v-for="item in listClassOptions"
              :key="item.value"
              :label="item.label + '(' + item.value + ')'"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio
              v-for="dict in dict.type.sys_normal_disable"
              :key="dict.value"
              :label="dict.value"
            >{{dict.label}}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Remark" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="Please enter content"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">Confirm</el-button>
        <el-button @click="cancel">Cancel</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { listData, getData, delData, addData, updateData } from "@/api/system/dict/data"
import { optionselect as getDictOptionselect, getType } from "@/api/system/dict/type"

export default {
  name: "Data",
  dicts: ['sys_normal_disable'],
  data() {
    return {
      // Loading mask
      loading: true,
      // Selected array
      ids: [],
      // Non-single disabled
      single: true,
      // Non-multiple disabled
      multiple: true,
      // Show search conditions
      showSearch: true,
      // Total count
      total: 0,
      // Dict table data
      dataList: [],
      // Default Dict type
      defaultDictType: "",
      // Popup title
      title: "",
      // Whether to show popup
      open: false,
      // Data label display style
      listClassOptions: [
        {
          value: "default",
          label: "Default"
        },
        {
          value: "primary",
          label: "Primary"
        },
        {
          value: "success",
          label: "Success"
        },
        {
          value: "info",
          label: "Info"
        },
        {
          value: "warning",
          label: "Warning"
        },
        {
          value: "danger",
          label: "Danger"
        }
      ],
      // Type data Dict
      typeOptions: [],
      // Query parameters
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        dictType: undefined,
        dictLabel: undefined,
        status: undefined
      },
      // Form parameters
      form: {},
      // Form validation
      rules: {
        dictLabel: [
          { required: true, message: "Data label cannot be empty", trigger: "blur" }
        ],
        dictValue: [
          { required: true, message: "Data value cannot be empty", trigger: "blur" }
        ],
        dictSort: [
          { required: true, message: "Data sort cannot be empty", trigger: "blur" }
        ]
      }
    }
  },
  created() {
    const dictId = this.$route.params && this.$route.params.dictId
    this.getType(dictId)
    this.getTypeList()
  },
  methods: {
    /** Query Dict type details */
    getType(dictId) {
      getType(dictId).then(response => {
        this.queryParams.dictType = response.data.dictType
        this.defaultDictType = response.data.dictType
        this.getList()
      })
    },
    /** Query Dict type list */
    getTypeList() {
      getDictOptionselect().then(response => {
        this.typeOptions = response.data
      })
    },
    /** Query Dict data list */
    getList() {
      this.loading = true
      listData(this.queryParams).then(response => {
        this.dataList = response.rows
        this.total = response.total
        this.loading = false
      })
    },
    // Cancel button
    cancel() {
      this.open = false
      this.reset()
    },
    // Form reset
    reset() {
      this.form = {
        dictCode: undefined,
        dictLabel: undefined,
        dictValue: undefined,
        cssClass: undefined,
        listClass: 'default',
        dictSort: 0,
        status: "0",
        remark: undefined
      }
      this.resetForm("form")
    },
    /** Search button operation */
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    /** Back button operation */
    handleClose() {
      const obj = { path: "/system/dict" }
      this.$tab.closeOpenPage(obj)
    },
    /** Reset button operation */
    resetQuery() {
      this.resetForm("queryForm")
      this.queryParams.dictType = this.defaultDictType
      this.handleQuery()
    },
    /** Add button operation */
    handleAdd() {
      this.reset()
      this.open = true
      this.title = "Add Dict Data"
      this.form.dictType = this.queryParams.dictType
    },
    // Multiple selection data
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.dictCode)
      this.single = selection.length!=1
      this.multiple = !selection.length
    },
    /** Edit button operation */
    handleUpdate(row) {
      this.reset()
      const dictCode = row.dictCode || this.ids
      getData(dictCode).then(response => {
        this.form = response.data
        this.open = true
        this.title = "Edit Dict Data"
      })
    },
    /** Submit button */
    submitForm: function() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.dictCode != undefined) {
            updateData(this.form).then(response => {
              this.$store.dispatch('dict/removeDict', this.queryParams.dictType)
              this.$modal.msgSuccess("Edit successful")
              this.open = false
              this.getList()
            })
          } else {
            addData(this.form).then(response => {
              this.$store.dispatch('dict/removeDict', this.queryParams.dictType)
              this.$modal.msgSuccess("Add successful")
              this.open = false
              this.getList()
            })
          }
        }
      })
    },
    /** Delete button operation */
    handleDelete(row) {
      const dictCodes = row.dictCode || this.ids
      this.$modal.confirm('Are you sure to delete the data item with Dict code "' + dictCodes + '"?').then(function() {
        return delData(dictCodes)
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess("Delete successful")
        this.$store.dispatch('dict/removeDict', this.queryParams.dictType)
      }).catch(() => {})
    },
    /** Export button operation */
    handleExport() {
      this.download('system/dict/data/export', {
        ...this.queryParams
      }, `data_${new Date().getTime()}.xlsx`)
    }
  }
}
</script>
