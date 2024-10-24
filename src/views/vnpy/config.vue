<template>
  <div class="app-container">
    <el-form ref="form" :model="form" label-width="200px" v-loading="loading">
      <el-row>
        <el-col :span="2">
          <el-form-item label="端口">{{ port }}</el-form-item>
        </el-col>
        <el-col :span="4">
          <el-form-item label="周期">{{ flag | period }}</el-form-item>
        </el-col>
        <el-col :span="9">
          <el-form-item label="模式">
            <el-select v-model="form.period.mode" placeholder="请选择">
              <el-option :key=1 :value=1 label="笔止盈"/>
              <el-option :key=2 :value=2 label="段止盈"/>
              <el-option :key=3 :value=3 label="趋势止盈"/>
            </el-select> 
          </el-form-item>
        </el-col>
        <el-col :span="9">
          <el-form-item label="中枢合并">
            <el-switch v-model="form.period.group" :active-value=1 :inactive-value=0 />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row v-for="(pivot, index) in form.pivots">
        <el-col :span="4">
          <el-form-item label="分级中枢数量统计">
            中枢等级{{ index + 1 }}：
          </el-form-item>
        </el-col>
        <el-col :span="10">
          <el-form-item label="中枢数量基本要求">
            <el-input type="number" v-model.number="pivot.count"/>
          </el-form-item>
        </el-col>
        <el-col :span="10">
          <el-form-item label="直接开仓中枢数量">
            <el-input type="number" v-model.number="pivot.limit"/>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <div style="width: 100%; text-align: center;">
      <el-button-group>
        <el-button type="primary" @click="save">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script>
import {config, action} from '@/api/vnpy'

export default {
  data() {
    return {
      datas: [],
      form: {},
      port: '',
      flag: '',
      loading: true
    }
  },
  mounted() {
    this.port = this.$route.params.port
    this.flag = this.$route.params.flag
    this.load()
  },
  methods: {
    load() {
      this.loading = true
      config(this.port).then(response => {
        this.loading = false
        this.datas = response.data
        this.form = this.datas[this.flag-1]
      })
    },
    save() {
      this.loading = true
      this.datas[this.flag-1] = this.form
      action({'action': 'config', 'port': this.port, 'content': this.datas}).then(response => {
        this.loading = false
      })
    }
  },
  filters: {
      period(flag) {
        const map = {
            1: '一分钟',
            2: '五分钟',
            3: '三十分钟'
        }
        return map[flag]
      }
  }
}
</script>

<style scoped>
</style>
