import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'mijiaAPI',
  description: '米家设备的 Python API',
  lastUpdated: true,
  cleanUrls: true,

  head: [
    ['link', { rel: 'icon', type: 'image/png', href: '/logo.png' }],
  ],

  themeConfig: {
    logo: '/logo.png',

    nav: [
      { text: '指南', link: '/guide/introduction' },
      { text: '使用', link: '/usage/basic-api' },
      { text: 'API 参考', link: '/reference/mijia-api' },
      { text: '常见问题', link: '/faq' },
      {
        text: '更多',
        items: [
          { text: '更新日志', link: '/changelog' },
          { text: '关于', link: '/about' },
          { text: 'GitHub', link: 'https://github.com/Do1e/mijia-api' },
        ],
      },
    ],

    sidebar: {
      '/guide/': [
        {
          text: '指南',
          items: [
            { text: '项目简介', link: '/guide/introduction' },
            { text: '安装', link: '/guide/installation' },
            { text: '快速开始', link: '/guide/quickstart' },
          ],
        },
      ],
      '/usage/': [
        {
          text: '使用',
          items: [
            { text: 'API 基础使用', link: '/usage/basic-api' },
            { text: 'mijiaDevice 高级封装', link: '/usage/mijia-device' },
            { text: 'CLI 命令行', link: '/usage/cli' },
            { text: 'MCP Server', link: '/usage/mcp' },
            { text: '最佳实践', link: '/usage/best-practices' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'API 参考',
          items: [
            { text: 'mijiaAPI 类', link: '/reference/mijia-api' },
            { text: 'mijiaDevice 类', link: '/reference/mijia-device' },
            { text: '异常与错误码', link: '/reference/errors' },
            { text: 'CLI 参数参考', link: '/reference/cli-args' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Do1e/mijia-api' },
    ],

    footer: {
      message: '基于 GPL-3.0 许可证发布',
      copyright: 'Copyright © 2024-2026 Do1e',
    },

    outline: {
      label: '本页目录',
    },

    docFooter: {
      prev: '上一页',
      next: '下一页',
    },

    lastUpdated: {
      text: '最后更新于',
    },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
  },
})
