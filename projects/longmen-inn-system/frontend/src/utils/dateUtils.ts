/**
 * 龙门客栈业务管理系统 - 日期工具函数
 * 基于 dayjs 的日期处理工具
 */

// 第一步：导入 dayjs
import * as dayjs from 'dayjs'

// 第二步：导入插件和语言包
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

// 第三步：注册插件（必须在调用 dayjs 方法之前完成）
dayjs.extend(relativeTime)

// 第四步：设置语言
// 使用中文本地化
const dayjsWithLocale = dayjs.locale('zh-cn')

/**
 * 获取相对时间（如：2小时前、3天前）
 * @param date 日期字符串或 Date 对象
 * @returns 相对时间字符串
 */
export function getRelativeTime(date: string | Date): string {
  if (!date) return ''
  try {
    return dayjs(date).fromNow()
  } catch (error) {
    console.error('getRelativeTime error:', error)
    return ''
  }
}

/**
 * 格式化日期
 * @param date 日期字符串或 Date 对象
 * @param format 格式化字符串，默认为 'YYYY-MM-DD HH:mm'
 * @returns 格式化后的日期字符串
 */
export function formatDate(
  date: string | Date,
  format = 'YYYY-MM-DD HH:mm'
): string {
  if (!date) return ''
  try {
    return dayjs(date).format(format)
  } catch (error) {
    console.error('formatDate error:', error)
    return ''
  }
}

/**
 * 格式化日期（仅日期部分）
 * @param date 日期字符串或 Date 对象
 * @returns 格式化后的日期字符串 YYYY-MM-DD
 */
export function formatDateOnly(date: string | Date): string {
  return formatDate(date, 'YYYY-MM-DD')
}

/**
 * 获取当前时间戳
 * @returns 当前时间戳（毫秒）
 */
export function getCurrentTimestamp(): number {
  return dayjs().valueOf()
}

/**
 * 获取当前时间字符串
 * @param format 格式化字符串
 * @returns 当前时间字符串
 */
export function getCurrentTime(format = 'YYYY-MM-DD HH:mm:ss'): string {
  return dayjs().format(format)
}

/**
 * 判断日期是否为今天
 * @param date 日期字符串或 Date 对象
 * @returns 是否为今天
 */
export function isToday(date: string | Date): boolean {
  if (!date) return false
  try {
    return dayjs(date).isSame(dayjs(), 'day')
  } catch (error) {
    console.error('isToday error:', error)
    return false
  }
}

/**
 * 判断日期是否过期（早于今天）
 * @param date 日期字符串或 Date 对象
 * @returns 是否已过期
 */
export function isExpired(date: string | Date): boolean {
  if (!date) return false
  try {
    return dayjs(date).isBefore(dayjs(), 'day')
  } catch (error) {
    console.error('isExpired error:', error)
    return false
  }
}

/**
 * 添加天数
 * @param date 日期字符串或 Date 对象
 * @param days 要添加的天数
 * @returns 新的日期对象
 */
export function addDays(date: string | Date, days: number): Date {
  try {
    return dayjs(date).add(days, 'day').toDate()
  } catch (error) {
    console.error('addDays error:', error)
    return new Date()
  }
}

/**
 * 计算两个日期之间的天数差
 * @param date1 第一个日期
 * @param date2 第二个日期
 * @returns 天数差
 */
export function diffDays(date1: string | Date, date2: string | Date): number {
  try {
    return dayjs(date1).diff(dayjs(date2), 'day')
  } catch (error) {
    console.error('diffDays error:', error)
    return 0
  }
}

// 默认导出 dayjs 实例
export default dayjs