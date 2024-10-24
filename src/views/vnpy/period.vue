<template>
  <div class="app-container">
    <el-table v-loading="loading " :data="data" element-loading-text="Loading" border fit highlight-current-row>
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
      <el-table-column label="代码" align="center">
        <template slot-scope="scope">
          {{ scope.row.code }}
        </template>
      </el-table-column>
      <el-table-column label="操作端口" align="center">
        <template slot-scope="scope">
          {{ scope.row.port }}
        </template>
      </el-table-column>
      <el-table-column label="一分钟" align="center">
        <template slot-scope="scope">
          <router-link :to="'/vnpy/edit/'+scope.row.port+'/'+scope.row.min1">设置</router-link>
        </template>
      </el-table-column>
      <el-table-column label="五分钟" align="center">
        <template slot-scope="scope">
          <router-link :to="'/vnpy/edit/'+scope.row.port+'/'+scope.row.min5">设置</router-link>
        </template>
      </el-table-column>
      <el-table-column label="三十分钟" align="center">
        <template slot-scope="scope">
          <router-link :to="'/vnpy/edit/'+scope.row.port+'/'+scope.row.min30">设置</router-link>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      data: [
        {post: 1, name: '沪深', code: 'if', port: 8125, min1: 1, min5: 2, min30: 3},
        {post: 2, name: '上证', code: 'ih', port: 8126, min1: 1, min5: 2, min30: 3},
        {post: 3, name: '中证', code: 'ic', port: 8127, min1: 1, min5: 2, min30: 3},
        {post: 4, name: '中千', code: 'im', port: 8128, min1: 1, min5: 2, min30: 3}
      ],
      loading: false
    }
  },
  created() {
  },
  methods: {
  }
}
</script>

<style scoped>
</style>
