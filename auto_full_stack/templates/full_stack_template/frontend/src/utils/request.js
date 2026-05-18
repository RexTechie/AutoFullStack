import axios from 'axios'
import { Notification, MessageBox, Message, Loading } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'
import errorCode from '@/utils/errorCode'
import { tansParams, blobValidate } from "@/utils/ruoyi"
import cache from '@/plugins/cache'
import { saveAs } from 'file-saver'

let downloadLoadingInstance
// Whether to show re-login
export let isRelogin = { show: false }

axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8'
// Create axios instance
const service = axios.create({
  // axios request config has baseURL option, represents common part of request URL
  baseURL: process.env.VUE_APP_BASE_API,
  // Timeout
  timeout: 10000
})

// Request interceptor
service.interceptors.request.use(config => {
  // Whether to set token
  const isToken = (config.headers || {}).isToken === false
  // Whether to prevent duplicate data submission
  const isRepeatSubmit = (config.headers || {}).repeatSubmit === false
  if (getToken() && !isToken) {
    config.headers['Authorization'] = 'Bearer ' + getToken() // Let each request carry custom token, please modify according to actual situation
  }
  // GET request maps params parameters
  if (config.method === 'get' && config.params) {
    let url = config.url + '?' + tansParams(config.params)
    url = url.slice(0, -1)
    config.params = {}
    config.url = url
  }
  if (!isRepeatSubmit && (config.method === 'post' || config.method === 'put')) {
    const requestObj = {
      url: config.url,
      data: typeof config.data === 'object' ? JSON.stringify(config.data) : config.data,
      time: new Date().getTime()
    }
    const requestSize = Object.keys(JSON.stringify(requestObj)).length // Request data size
    const limitSize = 5 * 1024 * 1024 // Limit stored data to 5M
    if (requestSize >= limitSize) {
      console.warn(`[${config.url}]: ` + 'Request data size exceeds allowed 5M limit, cannot perform duplicate submission verification.')
      return config
    }
    const sessionObj = cache.session.getJSON('sessionObj')
    if (sessionObj === undefined || sessionObj === null || sessionObj === '') {
      cache.session.setJSON('sessionObj', requestObj)
    } else {
      const s_url = sessionObj.url                  // Request address
      const s_data = sessionObj.data                // Request data
      const s_time = sessionObj.time                // Request time
      const interval = 1000                         // Interval time (ms), less than this time is considered duplicate submission
      if (s_data === requestObj.data && requestObj.time - s_time < interval && s_url === requestObj.url) {
        const message = 'Data is being processed, please do not submit repeatedly'
        console.warn(`[${s_url}]: ` + message)
        return Promise.reject(new Error(message))
      } else {
        cache.session.setJSON('sessionObj', requestObj)
      }
    }
  }
  return config
}, error => {
    console.log(error)
    Promise.reject(error)
})

// Response interceptor
service.interceptors.response.use(res => {
    // If no status code is set, default to success status
    const code = res.data.code || 200
    // Get error message
    const msg = errorCode[code] || res.data.msg || errorCode['default']
    // Binary data returns directly
    if (res.request.responseType ===  'blob' || res.request.responseType ===  'arraybuffer') {
      return res.data
    }
    if (code === 401) {
      if (!isRelogin.show) {
        isRelogin.show = true
        MessageBox.confirm('Login status has expired, you can continue to stay on this page, or log in again', 'System Prompt', { confirmButtonText: 'Re-login', cancelButtonText: 'Cancel', type: 'warning' }).then(() => {
          isRelogin.show = false
          store.dispatch('LogOut').then(() => {
            location.href = '/index'
          })
      }).catch(() => {
        isRelogin.show = false
      })
    }
      return Promise.reject('Invalid session, or session has expired, please log in again.')
    } else if (code === 500) {
      Message({ message: msg, type: 'error' })
      return Promise.reject(new Error(msg))
    } else if (code === 601) {
      Message({ message: msg, type: 'warning' })
      return Promise.reject('error')
    } else if (code !== 200) {
      Notification.error({ title: msg })
      return Promise.reject('error')
    } else {
      return res.data
    }
  },
  error => {
    console.log('err' + error)
    let { message } = error
    if (message == "Network Error") {
      message = "Backend interface connection exception"
    } else if (message.includes("timeout")) {
      message = "System interface request timeout"
    } else if (message.includes("Request failed with status code")) {
      message = "System interface " + message.substr(message.length - 3) + " exception"
    }
    Message({ message: message, type: 'error', duration: 5 * 1000 })
    return Promise.reject(error)
  }
)

// General download method
export function download(url, params, filename, config) {
  downloadLoadingInstance = Loading.service({ text: "Downloading data, please wait", spinner: "el-icon-loading", background: "rgba(0, 0, 0, 0.7)", })
  return service.post(url, params, {
    transformRequest: [(params) => { return tansParams(params) }],
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    responseType: 'blob',
    ...config
  }).then(async (data) => {
    const isBlob = blobValidate(data)
    if (isBlob) {
      const blob = new Blob([data])
      saveAs(blob, filename)
    } else {
      const resText = await data.text()
      const rspObj = JSON.parse(resText)
      const errMsg = errorCode[rspObj.code] || rspObj.msg || errorCode['default']
      Message.error(errMsg)
    }
    downloadLoadingInstance.close()
  }).catch((r) => {
    console.error(r)
    Message.error('Error downloading file, please contact administrator!')
    downloadLoadingInstance.close()
  })
}

export default service
