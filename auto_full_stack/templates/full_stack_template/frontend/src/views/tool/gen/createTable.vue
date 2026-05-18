<template>
  <!-- Create Table -->
  <el-dialog title="Create Table" :visible.sync="visible" width="800px" top="5vh" append-to-body>
    <span>Create Table Statement (supports multiple table creation statements):</span>
    <el-input type="textarea" :rows="10" placeholder="Please enter text" v-model="content"></el-input>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="handleCreateTable">Confirm</el-button>
      <el-button @click="visible = false">Cancel</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { createTable } from "@/api/tool/gen"
export default {
  data() {
    return {
      // Loading mask
      visible: false,
      // Text content
      content: ""
    }
  },
  methods: {
    // Show dialog
    show() {
      this.visible = true
    },
    /** Create button operation */
    handleCreateTable() {
      if (this.content === "") {
        this.$modal.msgError("Please enter table creation statement")
        return
      }
      createTable({ sql: this.content }).then(res => {
        this.$modal.msgSuccess(res.msg)
        if (res.code === 200) {
          this.visible = false
          this.$emit("ok")
        }
      })
    }
  }
}
</script>
