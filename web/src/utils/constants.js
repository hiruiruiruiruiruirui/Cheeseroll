// utils/constants.js — App-wide constants

export const API_BASE_URL = '/api/v1'

export const PLANS = [
  {
    type: 'daily',
    name: '包天',
    price: '¥9.9',
    priceCents: 990,
    duration: '1 天',
    features: ['单次资料整理', 'PDF 导出 1 次'],
    recommended: false,
  },
  {
    type: 'monthly',
    name: '包月',
    price: '¥49',
    priceCents: 4900,
    duration: '30 天',
    features: ['不限次数整理', '不限次导出', '多格式支持'],
    recommended: true,
  },
  {
    type: 'quarterly',
    name: '包季度',
    price: '¥99',
    priceCents: 9900,
    duration: '90 天',
    features: ['不限次数整理', '不限次导出', '多格式支持', '错题本', '进度追踪'],
    recommended: false,
  },
]

export const SUPPORTED_FORMATS = ['pptx', 'docx', 'pdf']
export const MAX_FILE_SIZE_MB = 50

export const PROGRESS_MAP = {
  queued: { progress: 5, text: '排队中...' },
  parsing: { progress: 20, text: '正在解析文档...' },
  generating: { progress: 60, text: 'AI 正在整理笔记...' },
  exporting: { progress: 90, text: '正在生成 PDF...' },
  completed: { progress: 100, text: '完成！' },
  failed: { progress: 0, text: '处理失败' },
}
