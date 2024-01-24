<template>
  <div class="ai-chat">
    <div class="chat-container">
      <div ref="messages" class="messages">
        <div v-if="messages.length === 0" class="empty-message">
            <img src="../../icons/logo2.png" alt="logo" style="height: 10%;width: 20%;"/>
            Forecast the traffic with AI
        </div>
        <div v-for="message in messages" :key="message.id" class="message">
            <div class="message-header">
                <img :src="message.avatar" alt="avatar" class="avatar">
                <p style="font-weight: bold;">{{ message.name }}</p>
            </div>
            <p style="white-space: pre-wrap;margin-left: 35px;margin-top: -10px;">{{ message.text }}</p>
        </div>
      </div>

      <div class="input-area">
        <el-button style="margin-right: 10px;" @click="dialogFormVisible = true">
          <el-icon name="upload"></el-icon>
        </el-button>
        <el-input
          v-model="newMessage"
          placeholder="请先上传数据集，然后输入您的需求(Ctrl+Enter换行)..."
          type="textarea"
          autofocus="true"
          maxlength="2000"
          resize="none"
          show-word-limit
          @keydown.native="handleKeyCode($event)"
        />
        <el-button v-if="noSend === true" style="margin-left: 10px;" @click="sendMessage">
          <el-icon name="s-promotion"></el-icon>
        </el-button>
        <el-button v-else style="margin-left: 10px;" disabled>
          <el-icon name="s-promotion"></el-icon>
        </el-button>
        <el-button @click="clean">
          <el-icon name="delete"></el-icon>
        </el-button>
      </div>
    </div>
    <el-dialog
      :destroy-on-close="true"
      :title="$t('dataset.fileUpload')"
      :visible.sync="dialogFormVisible"
    >
      <div style="margin: 0 auto">
        <el-form ref="uploadForm" :model="uploadForm">
          <el-form-item :label="$t('dataset.isPublic')" prop="isPublic">
            <el-switch
              v-model="uploadForm.isPublic"
              :active-text="$t('dataset.public')"
              :inactive-text="$t('dataset.private')"
            />
          </el-form-item>
          <el-form-item :label="$t('dataset.selectFile')">
            <el-upload
              ref="elupload"
              :action="BASE_API + '/business/file/'"
              name="dataset"
              :data="uploadForm"
              :headers="uploadHeaders"
              :file-list="filelist"
              multiple
              drag
              :auto-upload="false"
              :on-success="handleFileUploadSuccess"
              :before-upload="handleBeforeUpload"
              accept="application/x-zip-compressed"
            >
              <i class="el-icon-upload" />
              <div class="el-upload__text">{{ $t('dataset.clickUpload') }}</div>
              <div slot="tip" class="el-upload__tip">{{ $t('dataset.aiUploadTips') }}</div>
            </el-upload>
          </el-form-item>
          <el-row :gutter="20" type="flex" justify="center">
            <el-col :span="6">
              <el-button type="primary" size="medium" @click="submitUpload">{{ $t('dataset.submit') }}</el-button>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" size="medium" @click="dialogFormVisible = false">{{ $t('common.cancel') }}</el-button>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getToken } from '@/utils/auth'
import { updateFileVisibility } from '@/api/file'
import i18n from '@/lang'
import axios from 'axios'

export default {
  data() {
    return {
      BASE_API: window.global_url.Base_url,
      messages: [],
      newMessage: '',
      uploadForm: {
        isPublic: false
      }, // 上传表单数据对象
      uploadHeaders: {
        'Authorization': 'Bearer ' + getToken()
      },
      dialogFormVisible: false,
      filelist: [],
      noSend: true
    }
  },
  methods: {
    sendMessage() {
      this.messages.push({
        id: this.messages.length,
        text: this.newMessage,
        avatar: this.$store.getters.avatar,
        name: 'You'
      })
      this.messages.push({
        id: this.messages.length,
        text: '',
        name: 'LibCity',
        avatar: require('../../icons/logo.png')
      })
      this.noSend = false
      let ellipsisCount = 1
      const intervalId = setInterval(() => {
        ellipsisCount = ellipsisCount + 1
        if (ellipsisCount % 2 === 1) {
          this.messages[this.messages.length - 1].text = '●'
        } else {
          this.messages[this.messages.length - 1].text = ''
        }
      }, 500)
      // 向后端发送请求
      axios.post(this.BASE_API + '/aichat/', { message: this.newMessage })
        .then(response => {
          clearInterval(intervalId)
          this.messages[this.messages.length - 1].text = ''
          this.noSend = true
          let i = 0
          const typingInterval = setInterval(() => {
            if (i < response.data.message.length) {
              if (this.messages[this.messages.length - 1].text.endsWith('●')) {
                this.messages[this.messages.length - 1].text = this.messages[this.messages.length - 1].text.slice(0, -1)
              }
              // 添加新的字符和黑色圆点
              this.messages[this.messages.length - 1].text += response.data.message[i] + '●'
              this.$nextTick(() => {
                const container = this.$refs.messages
                container.scrollTop = container.scrollHeight
              })
              i++
            } else {
              // 移除最后一个黑色圆点
              if (this.messages[this.messages.length - 1].text.endsWith('●')) {
                this.messages[this.messages.length - 1].text = this.messages[this.messages.length - 1].text.slice(0, -1)
              }
              clearInterval(typingInterval)
            }
          }, 50)
        })
        .catch(error => {
          console.error(error)
        })
      this.newMessage = ''
    },
    clean() {
      this.messages = []
    },
    handleKeyCode(e) {
      if (e.keyCode === 13) {
        if (!e.ctrlKey) {
          e.preventDefault()
          this.sendMessage()
        } else {
          this.newMessage += '\n'
        }
      }
    },
    // 公开私有按钮改变
    visibilitySwitchChange(newValue, datasetId) {
      updateFileVisibility(datasetId, newValue).then(res => {
        this.getList(this.queryParam)
      })
    },
    // 提交确认上传
    submitUpload() {
      this.$refs.elupload.submit()
    },
    handleBeforeUpload(file) {
      // var isZip = file.type === 'application/x-zip-compressed'  // bug mac 上不能识别
      // 因为 .zip 格式可以有很多种：application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip
      // 所以这里直接判断包含 zip 字符串即可
      // 判断 file.type 是否包含 zip 字符串
      var isZip = file.type.includes('zip')
      if (!isZip) {
        this.$message.error(this.$t('dataset.uploadError'))
      }
      return isZip
    },
    handleFileUploadSuccess(response, file, filelist) {
      if (response.code >= 200 && response.code <= 300) {
        this.$message.success(this.$t('dataset.uploadSuccess'))
        // 遍历 filelist 判断 filelist 每个 item percentage 是否都为 100
        const allCompleted = filelist.every(item => {
          if (item.percentage === 100) {
            return true
          } else {
            return false
          }
        })
        if (allCompleted) {
          this.dialogFormVisible = false
        }
        this.getList(this.queryParam)
        this.title = i18n.t('dataset.canView')
        this.message = i18n.t('dataset.canViewSuccessfully')
        this.longPolling(response.data.id)
      } else if (response.code === 400) {
        // 数据集文件错误
        file.status = 'error'
        // 清空filelist
        filelist.splice(0, filelist.length)
        this.$message.error(this.$t('dataset.atomicError'))
      } else if (response.code === 409) {
        // 数据集重复
        file.status = 'error'
        // 清空filelist
        filelist.splice(0, filelist.length)
        this.$message.error(this.$t('dataset.datasetRepeatError'))
      }
    }
  }
}
</script>

<style scoped>
.ai-chat {
  display: flex;
  height: 100vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-image: url("../../icons/traffic.jpg");
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
}

.chat-container {
  margin: 40px;
  width: 80%;
  max-width: 1000px;
}

.messages {
  height: 500px;
  overflow-y: auto;
  border: 5px solid rgba(255, 255, 255, 0.3);
  padding: 10px;
  margin-bottom: 25px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(2px);
}

.input-area {
  display: flex;
  justify-content: space-between;
}

.avatar {
    border-radius: 50%;
    width: 30px;
    height: 30px;
    object-fit: cover;
    margin-right: 5px;
}

.message {
    display: flex;
    flex-direction: column;
}

.message-header {
    display: flex;
    align-items: center;
}

.empty-message {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-size: 25px;
    font-style: italic;
    font-weight: bold;
    color: #1c1c1c;
}
</style>
