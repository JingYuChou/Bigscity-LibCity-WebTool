<template>
  <div class="ai-chat" ref="aiChat">
    <div class="chat-container">
      <div ref="messages" class="messages">
        <div v-if="messages.length === 0" class="empty-message">
            <img src="../../icons/logo2.png" alt="logo" style="height: 10%;width: 20%;margin-bottom: 5px;"/>
            What can I do for you?
            <div class="pop" v-if="messages.length === 0">
                <div class="pop-column">
                  <Transition name="fade">
                    <div v-show="textVisible" class="pop-text">
                      <span style="font-weight: bold;">Traffic State Prediction</span> 
                      <span style="color: #7d7d89;">Forecaste future conditions and situations of traffic</span>
                    </div>
                  </Transition>
                  <Transition name="fade2">
                    <div v-show="textVisible" class="pop-text">
                      <span style="font-weight: bold;">Next Hop Prediction for Trajectories</span> 
                      <span style="color: #7d7d89;">Predicte the next step or location in a sequence of ...</span>
                    </div>
                  </Transition>
                </div>
                <div class="pop-column">
                  <Transition name="fade3">
                    <div v-show="textVisible" class="pop-text">
                      <span style="font-weight: bold;">Road Network Representation Learning</span> 
                      <span style="color: #7d7d89;">Capture and represent the essential features and ...</span>
                    </div>
                  </Transition>
                  <Transition name="fade4">
                    <div v-show="textVisible" class="pop-text">
                      <span style="font-weight: bold;">Road Network Matching</span> 
                      <span style="color: #7d7d89;">Associate collected location or trajectory data ...</span>
                    </div>
                  </Transition>
                </div>
            </div>
        </div>
        <div v-for="message in messages" :key="message.id" class="message">
            <div class="message-header">
                <img :src="message.avatar" alt="avatar" class="avatar">
                <p style="font-weight: bold;">{{ message.name }}</p>
            </div>
            <p style="white-space: pre-wrap;margin-left: 35px;margin-top: -10px;line-height: 1.5;">{{ message.text }}</p>
        </div>
      </div>
      <div class="input-area">
        <div class="message-buttons">
          <el-button class="message-button" style="margin-left: 10px;" @click="dialogFormVisible = true">
            <el-icon name="upload" class="message-icon"></el-icon>
          </el-button>
          <el-button v-if="noSend === true" ref="sendButton" class="message-button" style="margin-left: 10px;" @click="sendMessage">
            <el-icon name="s-promotion" class="message-icon"></el-icon>
          </el-button>
          <el-button v-else class="message-button" style="margin-left: 10px;" disabled>
            <el-icon name="s-promotion" class="message-icon"></el-icon>
          </el-button>
          <el-button class="message-button" @click="clean">
            <el-icon name="delete" class="message-icon"></el-icon>
          </el-button>
        </div>
        <el-input
          v-model="newMessage"
          placeholder="Message LibCity..."
          class="message-input"
          type="textarea"
          autofocus="true"
          maxlength="2000"
          resize="none"
          :autosize="{minRows:1,maxRows:4}"
          @keydown.native="handleKeyCode($event)"
        />
        <p style="display: flex;justify-content: center;color: #c5c5d2;font-size: .75rem;">Upload the dataset first, then tell LibCity what you need.</p>
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
      noSend: true,
      textVisible: false
    }
  },
  created() {
    setTimeout(() => {
      this.textVisible = true
    }, 1000)
  },
  methods: {
    sendMessage() {
      if (this.newMessage === '') {
        return
      }
      this.messages.push({
        id: this.messages.length,
        text: this.newMessage,
        // avatar: this.$store.getters.avatar,
        avatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        name: 'You'
      })
      this.messages.push({
        id: this.messages.length,
        text: '',
        name: 'LibCity',
        avatar: require('../../icons/logo.png')
      })
      this.noSend = false
      let ellipsisCount = 0
      const intervalId = setInterval(() => {
        ellipsisCount = ellipsisCount + 1
        if (ellipsisCount % 2 === 1) {
          this.messages[this.messages.length - 1].text = '●'
        } else {
          this.messages[this.messages.length - 1].text = ''
        }
      }, 1000)
      // 向后端发送请求
      axios.post(this.BASE_API + '/business/task/auto_create/', {
        message: this.newMessage,
        user_id: this.$store.getters.name
      })
        .then(response => {
          clearInterval(intervalId)
          this.messages[this.messages.length - 1].text = ''
          this.noSend = true
          let i = 0
          console.log(response)
          const typingInterval = setInterval(() => {
            if (i < response.data.data.message.length) {
              if (this.messages[this.messages.length - 1].text.endsWith('●')) {
                this.messages[this.messages.length - 1].text = this.messages[this.messages.length - 1].text.slice(0, -1)
              }
              // 添加新的字符和黑色圆点
              this.messages[this.messages.length - 1].text += response.data.data.message[i] + '●'
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
              this.$nextTick(() => {
                const container = this.$refs.messages
                container.scrollTop = container.scrollHeight
              })
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
  background-color: #353541;
  color: #ffffff;
  font-size: 1rem;
}

.chat-container {
  margin: 40px;
  width: 60%;
  max-width: 800px;
}

.messages {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
  border-radius: 5px;
}

.input-area {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: absolute;
  bottom: 0.5%;
  left: 20%;
  right: 20%;
}

.message-buttons {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 10px;
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
    margin-bottom: 10px;
}

.message-header {
    display: flex;
    align-items: center;
}

.message-icon {
    color: #c5c5d2;
    font-size: 16px;
}
.empty-message {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 80%;
    font-size: 1.4rem;
    font-weight: bold;
    color: #ffffff;
}

.message-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
    border-radius: 15px;
    background: #4A4A54;
    border: solid 1px rgba(74, 74, 84, 1);
}

.message-button:hover {
  background-color: #353541;
}

.pop {
    display: flex;
    background: transparent;
    width: 90%;
    margin-top: 7%;
}

.pop-column {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    background: transparent;
    width: 50%;
}

@keyframes jump {
      0%{
        transform: scale(0);
      }
      100% {
        transform: scale(1);
      }
    }

.pop-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
    font-size: .8rem;
    font-weight: normal;
    line-height: 1.5;
    color: #c5c5d2;
    border: solid 1px #565869;
    padding: 15px;
    border-radius: 15px;
    width: 98%;
    height: 44%;
    transition: background-color 0.3s ease;
}

.pop-text:hover {
    background-color: #40414f;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
  animation: jump 0.3s ease;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

.fade2-enter-active, .fade2-leave-active {
  transition: opacity 0.5s, transform 0.5s;
  animation: jump 0.5s ease;
}
.fade2-enter, .fade2-leave-to {
  opacity: 0;
}

.fade3-enter-active, .fade3-leave-active {
  transition: opacity 0.7s, transform 0.7s;
  animation: jump 0.7s ease;
}
.fade3-enter, .fade3-leave-to {
  opacity: 0;
}

.fade4-enter-active, .fade4-leave-active {
  transition: opacity 0.9s, transform 0.9s;
  animation: jump 0.9s ease;
}
.fade4-enter, .fade4-leave-to {
  opacity: 0;
}
.el-textarea{
  border-radius: 15px;
  background-color: #353541;
}

/deep/ .el-textarea__inner {
  background-color: transparent;
  border-radius: 15px;
  border: solid 1px rgba(74, 74, 84, 1);
  color: #ffffff;
  font-size: 1rem;
  padding: 15px;
}
/deep/ .el-textarea__inner::-webkit-scrollbar {
          width: 7px;
          height: 7px;
        }
        /*滚动条的轨道*/
        /deep/ .el-textarea__inner::-webkit-scrollbar-track {
          background-color: transparent;
        }
        /*滚动条里面的小方块，能向上向下移动*/
        /deep/ .el-textarea__inner::-webkit-scrollbar-thumb {
          background-color: rgba(144, 147, 153, 0.3);
          border-radius: 5px;
          box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.1);
        }
        /deep/ .el-textarea__inner::-webkit-scrollbar-thumb:hover {
          background-color: rgba(144, 147, 153, 0.3);
        }
        /deep/ .el-textarea__inner::-webkit-scrollbar-thumb:active {
          background-color: rgba(144, 147, 153, 0.3);
        }
        /*边角，即两个滚动条的交汇处*/
        /deep/ .el-textarea__inner::-webkit-scrollbar-corner {
          background-color: #ffffff;
        }

        .messages::-webkit-scrollbar {
          width: 7px;
          height: 7px;
        }
        /*滚动条的轨道*/
        .messages::-webkit-scrollbar-track {
          background-color: transparent;
        }
        /*滚动条里面的小方块，能向上向下移动*/
        .messages::-webkit-scrollbar-thumb {
          background-color: rgba(144, 147, 153, 0.3);
          border-radius: 5px;
          box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.1);
        }
        .messages::-webkit-scrollbar-thumb:hover {
          background-color: rgba(144, 147, 153, 0.3);
        }
        .messages::-webkit-scrollbar-thumb:active {
          background-color: rgba(144, 147, 153, 0.3);
        }
        /*边角，即两个滚动条的交汇处*/
        .messages::-webkit-scrollbar-corner {
          background-color: #ffffff;
        }
</style>
