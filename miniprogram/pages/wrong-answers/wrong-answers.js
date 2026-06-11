// pages/wrong-answers/wrong-answers.js — Wrong answer book (quarterly only)
const app = getApp();

Page({
  data: {
    answers: [],
    subjects: [],
    activeSubject: '',
    loading: true,
    page: 1,
    total: 0,
    hasMore: false,
    showForm: false,
    editingId: null,
    // Form fields
    formSubject: '',
    formQuestion: '',
    formAnswer: '',
    formCorrectAnswer: '',
    submitting: false,
    // Quick add state
    quickAdd: false,
    quickQuestion: '',
    quickSubject: '',
  },

  onShow() {
    this.setData({ page: 1, answers: [] });
    this.loadWrongAnswers();
  },

  onReachBottom() {
    if (this.data.hasMore) {
      this.setData({ page: this.data.page + 1 });
      this.loadWrongAnswers();
    }
  },

  async loadWrongAnswers() {
    const token = await app.ensureLogin();
    if (!token) {
      this.setData({ loading: false });
      return;
    }

    if (this.data.page === 1) this.setData({ loading: true });

    try {
      const params = { page: this.data.page, page_size: 20 };
      if (this.data.activeSubject) params.subject = this.data.activeSubject;

      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/wrong-answers`,
        method: 'GET',
        data: params,
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode === 200) {
        const items = res.data.items || [];
        // Collect unique subjects
        const subjectSet = new Set(this.data.subjects);
        items.forEach(item => { if (item.subject) subjectSet.add(item.subject); });

        this.setData({
          answers: this.data.page === 1 ? items : [...this.data.answers, ...items],
          total: res.data.total,
          hasMore: this.data.answers.length + items.length < res.data.total,
          subjects: Array.from(subjectSet).sort(),
          loading: false,
        });
      }
    } catch (err) {
      console.error('Load wrong answers error:', err);
      if (err.message && err.message.includes('402')) {
        wx.showToast({ title: '错题本需包季度订阅', icon: 'none' });
      }
      this.setData({ loading: false });
    }
  },

  // Filter by subject
  filterSubject(e) {
    const subject = e.currentTarget.dataset.subject;
    this.setData({
      activeSubject: this.data.activeSubject === subject ? '' : subject,
      page: 1,
      answers: [],
    });
    this.loadWrongAnswers();
  },

  // Show add/edit form
  showAddForm() {
    this.setData({
      showForm: true,
      editingId: null,
      formSubject: this.data.activeSubject || '',
      formQuestion: '',
      formAnswer: '',
      formCorrectAnswer: '',
    });
  },

  // Edit an existing entry
  editAnswer(e) {
    const item = e.currentTarget.dataset.item;
    this.setData({
      showForm: true,
      editingId: item.id,
      formSubject: item.subject || '',
      formQuestion: item.question,
      formAnswer: item.answer || '',
      formCorrectAnswer: item.correct_answer || '',
    });
  },

  hideForm() {
    this.setData({ showForm: false, editingId: null });
  },

  // Submit form (add or update)
  async submitForm() {
    const { formQuestion } = this.data;
    if (!formQuestion.trim()) {
      wx.showToast({ title: '请输入题目', icon: 'none' });
      return;
    }

    const token = await app.ensureLogin();
    if (!token) return;

    this.setData({ submitting: true });

    const body = {
      subject: this.data.formSubject || null,
      question: this.data.formQuestion,
      answer: this.data.formAnswer || null,
      correct_answer: this.data.formCorrectAnswer || null,
      tags: [],
    };

    try {
      const url = this.data.editingId
        ? `${app.globalData.apiBaseUrl}/wrong-answers/${this.data.editingId}`
        : `${app.globalData.apiBaseUrl}/wrong-answers`;
      const method = this.data.editingId ? 'PUT' : 'POST';

      const res = await wx.request({
        url, method, data: body,
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode >= 200 && res.statusCode < 300) {
        wx.showToast({ title: this.data.editingId ? '已更新' : '已添加', icon: 'success' });
        this.hideForm();
        this.setData({ page: 1, answers: [] });
        this.loadWrongAnswers();
      } else {
        wx.showToast({ title: res.data?.detail || '操作失败', icon: 'none' });
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },

  // Delete an entry
  async deleteAnswer(e) {
    const id = e.currentTarget.dataset.id;
    const token = await app.ensureLogin();
    if (!token) return;

    wx.showModal({
      title: '确认删除',
      content: '确定要删除这道错题吗？',
      success: async (res) => {
        if (!res.confirm) return;
        try {
          const resp = await wx.request({
            url: `${app.globalData.apiBaseUrl}/wrong-answers/${id}`,
            method: 'DELETE',
            header: { Authorization: `Bearer ${token}` },
          });
          if (resp.statusCode === 204) {
            wx.showToast({ title: '已删除', icon: 'success' });
            this.setData({ page: 1, answers: [] });
            this.loadWrongAnswers();
          }
        } catch (err) {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      },
    });
  },

  // Quick add from text
  toggleQuickAdd() {
    this.setData({ quickAdd: !this.data.quickAdd });
  },

  async submitQuickAdd() {
    const { quickQuestion } = this.data;
    if (!quickQuestion.trim()) {
      wx.showToast({ title: '请输入题目', icon: 'none' });
      return;
    }

    const token = await app.ensureLogin();
    if (!token) return;

    this.setData({ submitting: true });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/wrong-answers`,
        method: 'POST',
        data: {
          question: quickQuestion,
          subject: this.data.quickSubject || null,
          tags: [],
        },
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode >= 200 && res.statusCode < 300) {
        wx.showToast({ title: '已添加', icon: 'success' });
        this.setData({ quickAdd: false, quickQuestion: '', quickSubject: '', page: 1, answers: [] });
        this.loadWrongAnswers();
      } else {
        wx.showToast({ title: '添加失败', icon: 'none' });
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },

  // AI generate similar question
  async generateSimilar(e) {
    const item = e.currentTarget.dataset.item;
    const token = await app.ensureLogin();
    if (!token) return;

    wx.showLoading({ title: 'AI 生成中...' });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/wrong-answers/generate-similar`,
        method: 'POST',
        data: {
          question: item.question,
          answer: item.answer || item.correct_answer || '',
          subject: item.subject || '',
        },
        header: { Authorization: `Bearer ${token}` },
      });

      wx.hideLoading();

      if (res.statusCode === 200) {
        const data = res.data;
        wx.showModal({
          title: 'AI 相似题',
          content: `${data.similar_question}\n\n参考答案：${data.answer || '无'}`,
          confirmText: '保存到错题本',
          cancelText: '关闭',
          success: async (modalRes) => {
            if (modalRes.confirm) {
              await wx.request({
                url: `${app.globalData.apiBaseUrl}/wrong-answers`,
                method: 'POST',
                data: {
                  question: data.similar_question,
                  answer: data.answer || '',
                  subject: item.subject || '',
                  tags: [],
                },
                header: { Authorization: `Bearer ${token}` },
              });
              wx.showToast({ title: '已保存', icon: 'success' });
              this.setData({ page: 1, answers: [] });
              this.loadWrongAnswers();
            }
          },
        });
      } else {
        wx.showToast({ title: '生成失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  },
});
