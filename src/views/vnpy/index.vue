<template>
  <div class="app-container">
    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column label="代码" align="center" width="95">
        <template slot-scope="scope">
          {{ scope.row.code }}
        </template>
      </el-table-column>
      <el-table-column label="位置" align="center" width="95">
        <template slot-scope="scope">
          {{ scope.row.post }}
        </template>
      </el-table-column>
      <el-table-column label="名称" align="center">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="操作端口" align="center">
        <template slot-scope="scope">
          {{ scope.row.port }}
        </template>
      </el-table-column>
      <el-table-column label="买卖量" align="center">
        <template slot-scope="scope">
          {{ scope.row.count }}
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="280">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="buy(scope.row.port)">买开</el-button>
          <el-button type="success" size="small" @click="short(scope.row.port)">卖开</el-button>
          <el-button type="success" size="small" @click="cover(scope.row.port)">买平</el-button>
          <el-button type="success" size="small" @click="sell(scope.row.port)">卖平</el-button>
        </template>
      </el-table-column>
      <el-table-column label="设置" align="center" width="200">
        <template slot-scope="scope">
          买开：<el-switch v-model="scope.row.buy" @change="set(scope.$index)"/>
          卖开：<el-switch v-model="scope.row.short" @change="set(scope.$index)"/>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import {list, operate, setting} from '@/api/vnpy'

export default {
  data() {
    return {
      list: null,
      listLoading: true
    }
  },
  created() {
    this.getStrategieList()
  },
  methods: {
    getStrategieList() {
      this.listLoading = true
      list().then(response => {
        this.listLoading = false
        this.list = response.data
      })
    },
    buy(port) {
      operate(port, 1, 9999, 99, 0)
    },
    short(port) {
      operate(port, 2, 9999, 99, 0)
    },
    cover(port) {
      operate(port, 3, 9999, 99, 0)
    },
    sell(port) {
      operate(port, 4, 9999, 99, 0)
    },
    set(index) {
      setting(this.list[index].port, this.list[index].buy ? 1 : 0, this.list[index].short ? 1 : 0)
    }
  }
}
</script>

<style scoped>
</style>
