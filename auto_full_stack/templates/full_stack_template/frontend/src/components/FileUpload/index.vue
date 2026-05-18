<template>
  <div class="upload-file">
    <el-upload
      multiple
      :action="uploadFileUrl"
      :before-upload="handleBeforeUpload"
      :file-list="fileList"
      :data="data"
      :limit="limit"
      :on-error="handleUploadError"
      :on-exceed="handleExceed"
      :on-success="handleUploadSuccess"
      :show-file-list="false"
      :headers="headers"
      class="upload-file-uploader"
      ref="fileUpload"
      v-if="!disabled"
    >
      <!-- Upload button -->
      <el-button size="mini" type="primary">Select File</el-button>
      <!-- Upload tip -->
      <div class="el-upload__tip" slot="tip" v-if="showTip">
        Please upload
        <template v-if="fileSize"> size not exceeding <b style="color: #f56c6c">{{ fileSize }}MB</b> </template>
        <template v-if="fileType"> format <b style="color: #f56c6c">{{ fileType.join("/") }}</b> </template>
        file
      </div>
    </el-upload>

    <!-- File list -->
    <transition-group ref="uploadFileList" class="upload-file-list el-upload-list el-upload-list--text" name="el-fade-in-linear" tag="ul">
      <li :key="file.url" class="el-upload-list__item ele-upload-list__item-content" v-for="(file, index) in fileList">
        <el-link :href="`${baseUrl}${file.url}`" :underline="false" target="_blank">
          <span class="el-icon-document"> {{ getFileName(file.name) }} </span>
        </el-link>
        <div class="ele-upload-list__item-content-action">
          <el-link :underline="false" @click="handleDelete(index)" type="danger" v-if="!disabled">Delete</el-link>
        </div>
      </li>
    </transition-group>
  </div>
</template>

<script>
import { getToken } from "@/utils/auth"
import Sortable from 'sortablejs'

export default {
  name: "FileUpload",
  props: {
    // Value
    value: [String, Object, Array],
    // Upload interface address
    action: {
      type: String,
      default: "/common/upload"
    },
    // Parameters carried by upload
    data: {
      type: Object
    },
    // Quantity limit
    limit: {
      type: Number,
      default: 5
    },
    // Size limit (MB)
    fileSize: {
      type: Number,
      default: 5
    },
    // File type, e.g. ['png', 'jpg', 'jpeg']
    fileType: {
      type: Array,
      default: () => ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "pdf"]
    },
    // Whether to show tip
    isShowTip: {
      type: Boolean,
      default: true
    },
    // Disable component (view files only)
    disabled: {
      type: Boolean,
      default: false
    },
    // Drag sorting
    drag: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      number: 0,
      uploadList: [],
      baseUrl: process.env.VUE_APP_BASE_API,
      uploadFileUrl: process.env.VUE_APP_BASE_API + this.action, // Upload file server address
      headers: {
        Authorization: "Bearer " + getToken(),
      },
      fileList: []
    }
  },
  mounted() {
    if (this.drag && !this.disabled) {
      this.$nextTick(() => {
        const element = this.$refs.uploadFileList?.$el || this.$refs.uploadFileList
        Sortable.create(element, {
          ghostClass: 'file-upload-darg',
          onEnd: (evt) => {
            const movedItem = this.fileList.splice(evt.oldIndex, 1)[0]
            this.fileList.splice(evt.newIndex, 0, movedItem)
            this.$emit("input", this.listToString(this.fileList))
          }
        })
      })
    }
  },
  watch: {
    value: {
      handler(val) {
        if (val) {
          let temp = 1
          // First convert value to array
          const list = Array.isArray(val) ? val : this.value.split(',')
          // Then convert array to object array
          this.fileList = list.map(item => {
            if (typeof item === "string") {
              item = { name: item, url: item }
            }
            item.uid = item.uid || new Date().getTime() + temp++
            return item
          })
        } else {
          this.fileList = []
          return []
        }
      },
      deep: true,
      immediate: true
    }
  },
  computed: {
    // Whether to show tip
    showTip() {
      return this.isShowTip && (this.fileType || this.fileSize)
    },
  },
  methods: {
    // Check format and size before upload
    handleBeforeUpload(file) {
      // Check file type
      if (this.fileType) {
        const fileName = file.name.split('.')
        const fileExt = fileName[fileName.length - 1]
        const isTypeOk = this.fileType.indexOf(fileExt) >= 0
        if (!isTypeOk) {
          this.$modal.msgError(`File format is incorrect, please upload ${this.fileType.join("/")} format file!`)
          return false
        }
      }
      // Check if file name contains special characters
      if (file.name.includes(',')) {
        this.$modal.msgError('File name is incorrect, cannot contain English comma!')
        return false
      }
      // Check file size
      if (this.fileSize) {
        const isLt = file.size / 1024 / 1024 < this.fileSize
        if (!isLt) {
          this.$modal.msgError(`Upload file size cannot exceed ${this.fileSize} MB!`)
          return false
        }
      }
      this.$modal.loading("Uploading file, please wait...")
      this.number++
      return true
    },
    // File count exceeded
    handleExceed() {
      this.$modal.msgError(`Upload file count cannot exceed ${this.limit}!`)
    },
    // Upload failed
    handleUploadError(err) {
      this.$modal.msgError("File upload failed, please try again")
      this.$modal.closeLoading()
    },
    // Upload success callback
    handleUploadSuccess(res, file) {
      if (res.code === 200) {
        this.uploadList.push({ name: res.fileName, url: res.fileName })
        this.uploadedSuccessfully()
      } else {
        this.number--
        this.$modal.closeLoading()
        this.$modal.msgError(res.msg)
        this.$refs.fileUpload.handleRemove(file)
        this.uploadedSuccessfully()
      }
    },
    // Delete file
    handleDelete(index) {
      this.fileList.splice(index, 1)
      this.$emit("input", this.listToString(this.fileList))
    },
    // Upload completion handling
    uploadedSuccessfully() {
      if (this.number > 0 && this.uploadList.length === this.number) {
        this.fileList = this.fileList.concat(this.uploadList)
        this.uploadList = []
        this.number = 0
        this.$emit("input", this.listToString(this.fileList))
        this.$modal.closeLoading()
      }
    },
    // Get file name
    getFileName(name) {
      // If it's a URL, get the last name, otherwise return directly
      if (name.lastIndexOf("/") > -1) {
        return name.slice(name.lastIndexOf("/") + 1)
      } else {
        return name
      }
    },
    // Convert object to specified string separator
    listToString(list, separator) {
      let strs = ""
      separator = separator || ","
      for (let i in list) {
        strs += list[i].url + separator
      }
      return strs != '' ? strs.substr(0, strs.length - 1) : ''
    }
  }
}
</script>

<style scoped lang="scss">
.file-upload-darg {
  opacity: 0.5;
  background: #c8ebfb;
}
.upload-file-uploader {
  margin-bottom: 5px;
}
.upload-file-list .el-upload-list__item {
  border: 1px solid #e4e7ed;
  line-height: 2;
  margin-bottom: 10px;
  position: relative;
}
.upload-file-list .ele-upload-list__item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: inherit;
}
.ele-upload-list__item-content-action .el-link {
  margin-right: 10px;
}
</style>
