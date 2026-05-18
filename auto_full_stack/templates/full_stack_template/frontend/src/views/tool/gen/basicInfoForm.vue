<template>
  <el-form ref="basicInfoForm" :model="info" :rules="rules" label-width="150px">
    <el-row>
      <el-col :span="12">
        <el-form-item label="Table Name" prop="tableName">
          <el-input placeholder="Please enter table name" v-model="info.tableName" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Table Description" prop="tableComment">
          <el-input placeholder="Please enter" v-model="info.tableComment" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Entity Class Name" prop="className">
          <el-input placeholder="Please enter" v-model="info.className" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Author" prop="functionAuthor">
          <el-input placeholder="Please enter" v-model="info.functionAuthor" />
        </el-form-item>
      </el-col>
      <el-col :span="24">
        <el-form-item label="Remark" prop="remark">
          <el-input type="textarea" :rows="3" v-model="info.remark"></el-input>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script>
export default {
  props: {
    info: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      rules: {
        tableName: [
          { required: true, message: "Please enter table name", trigger: "blur" }
        ],
        tableComment: [
          { required: true, message: "Please enter table description", trigger: "blur" }
        ],
        className: [
          { required: true, message: "Please enter entity class name", trigger: "blur" }
        ],
        functionAuthor: [
          { required: true, message: "Please enter author", trigger: "blur" }
        ]
      }
    }
  }
}
</script>
