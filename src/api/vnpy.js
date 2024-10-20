import request from '@/utils/request'

export function list() {
  return request({
    url: 'list',
    method: 'get'
  })
}

export function operate(port, key, flag, sign, stamp) {
  return request({
    url: 'vnpy',
    method: 'get',
    params: { 'port': port, 'key': key, 'flag': flag, 'sign': sign, 'stamp': stamp }
  })
}

export function setting(port, buy, short) {
  return request({
    url: 'setting',
    method: 'get',
    params: { 'port': port, 'buy': buy, 'short': short }
  })
}