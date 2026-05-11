import type { FormItemRule } from 'element-plus'

export const required = (label: string): FormItemRule => ({
  required: true, message: `${label}不能为空`, trigger: 'blur'
})

export const maxLength = (max: number): FormItemRule => ({
  max, message: `不能超过${max}个字符`, trigger: 'blur'
})

export const positiveNumber: FormItemRule = {
  type: 'number', min: 0, message: '必须为正数', trigger: 'blur'
}

export const phoneRule: FormItemRule = {
  pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur'
}
