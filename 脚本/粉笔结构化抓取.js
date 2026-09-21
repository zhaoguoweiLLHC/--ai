/**
 * 粉笔结构化真题批量抓取脚本 v2（反检测+断点续抓）
 * 
 * 反检测措施：
 * - 随机延迟（2-6秒），非固定间隔
 * - 模拟人类点击（先 hover 再 click，带随机偏移）
 * - 每抓几套随机停顿更久（模拟人走开）
 * - console.log 降频，避免刷屏暴露
 * - 断点续抓：中间断了可从上次位置继续
 * - 检测到异常弹窗/验证码自动暂停
 * 
 * 使用方法：
 * 1. 打开粉笔题库结构化列表页
 * 2. F12 → Console，粘贴此脚本回车
 * 3. 如中途断开，重新打开列表页再跑一次，自动从断点继续
 */

(async function () {
  'use strict';

  // ============ 反检测工具 ============

  // 随机延迟：min~max 毫秒，默认 2-6秒
  function randomDelay(min = 2000, max = 6000) {
    const ms = min + Math.random() * (max - min);
    return new Promise(r => setTimeout(r, ms));
  }

  // 短延迟：500-1500ms（页面内快速操作）
  function quickDelay() {
    return randomDelay(500, 1500);
  }

  // 模拟人类点击：先 hover 再 click
  function humanClick(el) {
    return new Promise(resolve => {
      // 先触发 mouseover（模拟鼠标移过去）
      const rect = el.getBoundingClientRect();
      const x = rect.left + rect.width * (0.3 + Math.random() * 0.4);
      const y = rect.top + rect.height * (0.3 + Math.random() * 0.4);

      el.dispatchEvent(new MouseEvent('mouseover', {
        bubbles: true, clientX: x, clientY: y
      }));

      // 停顿一下再点击
      setTimeout(() => {
        el.dispatchEvent(new MouseEvent('mousedown', {
          bubbles: true, clientX: x, clientY: y
        }));
        el.dispatchEvent(new MouseEvent('click', {
          bubbles: true, clientX: x, clientY: y
        }));
        el.dispatchEvent(new MouseEvent('mouseup', {
          bubbles: true, clientX: x, clientY: y
        }));

        // 如果是 Angular 组件，也触发原生 click
        if (el.click) el.click();

        resolve();
      }, 100 + Math.random() * 200);
    });
  }

  // 模拟人类滚动（让页面看起来有人在看）
  function humanScroll() {
    window.scrollTo({
      top: 100 + Math.random() * 300,
      behavior: 'smooth'
    });
  }

  // 检测异常：验证码/弹窗/被封提示
  function checkBlocked() {
    const body = document.body.innerText || '';
    const blockWords = ['验证', 'captcha', '安全验证', '请求过于频繁', '账号异常', '访问受限'];
    for (const w of blockWords) {
      if (body.includes(w)) {
        console.log('⚠️ 检测到可能的拦截提示：' + w);
        return true;
      }
    }
    // 检查是否有遮罩层弹窗
    const overlay = document.querySelector('[class*="modal"], [class*="dialog"], [class*="overlay"]');
    if (overlay && overlay.offsetParent !== null) {
      const overlayText = overlay.innerText || '';
      if (overlayText.includes('验证') || overlayText.includes('异常') || overlayText.includes('频繁')) {
        console.log('⚠️ 检测到弹窗拦截');
        return true;
      }
    }
    return false;
  }

  // 静默日志（减少控制台输出频率）
  let lastLogTime = 0;
  function log(msg, force = false) {
    const now = Date.now();
    if (force || now - lastLogTime > 3000) {
      console.log(msg);
      lastLogTime = now;
    }
  }

  // ============ 配置 ============
  const OUTPUT_KEY = 'fenbi_questions_result';
  const PROGRESS_KEY = 'fenbi_questions_progress';

  // 读取断点
  function loadProgress() {
    try {
      const raw = localStorage.getItem(PROGRESS_KEY);
      if (!raw) return { completedPapers: [], results: [], allPaperTitles: [] };
      return JSON.parse(raw);
    } catch (e) {
      return { completedPapers: [], results: [], allPaperTitles: [] };
    }
  }

  function saveProgress(progress) {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));
  }

  // ============ 第一步：收集所有试卷 ============
  function collectPapersFromCurrentPage() {
    const papers = [];
    const items = document.querySelectorAll('app-paper-item');
    items.forEach(item => {
      const titleEl = item.querySelector('.item-info-title');
      if (!titleEl) return;
      const title = titleEl.textContent.trim();
      const match = title.match(/试卷(\d+)/);
      const paperNum = match ? parseInt(match[1]) : null;
      const subtitleEl = item.querySelector('.item-info-subtitle');
      papers.push({
        title: title,
        paperNum: paperNum,
        difficulty: subtitleEl ? subtitleEl.textContent.trim() : '',
        element: item
      });
    });
    return papers;
  }

  async function collectAllPapers() {
    const allPapers = [];
    let visitedPages = new Set();

    while (true) {
      if (checkBlocked()) {
        console.log('⚠️ 收集试卷时检测到拦截，暂停。请手动处理后重新运行脚本。');
        return allPapers;
      }

      const papers = collectPapersFromCurrentPage();
      if (!papers.length) {
        log('当前页无试卷项');
        break;
      }

      // 去重添加
      papers.forEach(p => {
        if (!allPapers.find(a => a.title === p.title)) {
          allPapers.push(p);
        }
      });

      // 尝试翻页
      const pager = document.querySelector('fb-pager');
      if (!pager) break;

      const activePage = pager.querySelector('.active');
      const currentPageNum = activePage ? parseInt(activePage.textContent.trim()) : 1;
      visitedPages.add(currentPageNum);

      const allPageNums = Array.from(pager.querySelectorAll('.item')).map(el => {
        const t = el.textContent.trim();
        return /^\d+$/.test(t) ? parseInt(t) : null;
      }).filter(n => n !== null);
      const maxPage = allPageNums.length ? Math.max(...allPageNums) : 1;

      if (currentPageNum >= maxPage) break;

      // 找下一页按钮
      const items = Array.from(pager.querySelectorAll('.item'));
      const nextBtn = items[items.length - 1];

      if (nextBtn) {
        log(`翻到第${currentPageNum + 1}页...`);
        humanScroll();
        await quickDelay();
        await humanClick(nextBtn);
        await randomDelay(2500, 5000);

        // 验证翻页是否成功
        const newActive = document.querySelector('fb-pager .active');
        const newPageNum = newActive ? parseInt(newActive.textContent.trim()) : currentPageNum;
        if (visitedPages.has(newPageNum)) {
          log('翻页未生效，可能已到末页');
          break;
        }
        if (newPageNum <= currentPageNum) break;
      } else {
        break;
      }
    }

    return allPapers;
  }

  // ============ 第二步：提取单张试卷题目 ============
  async function extractQuestionsFromPaper(paper) {
    if (!paper.element || !paper.element.isConnected) {
      log(`DOM引用失效，跳过 ${paper.title}`);
      return null;
    }

    log(`打开 ${paper.title}...`);

    // 模拟人类操作：先滚动到元素位置再点击
    paper.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    await quickDelay();
    await humanClick(paper.element);

    // 随机等待页面加载（3-6秒）
    await randomDelay(3000, 6000);

    if (checkBlocked()) {
      console.log('⚠️ 抓取时检测到拦截，暂停。');
      return null;
    }

    // 等待题目渲染（最多等15秒）
    let retries = 0;
    while (retries < 10) {
      const solutions = document.querySelectorAll('app-fb-solution');
      if (solutions.length > 0) break;
      retries++;
      await quickDelay();
    }

    // 模拟人类浏览：先滚动看看
    humanScroll();
    await quickDelay();

    // 提取题目
    const questions = [];
    const solutionItems = document.querySelectorAll('app-fb-solution');

    solutionItems.forEach((sol, index) => {
      const question = {
        index: index + 1,
        type: '',
        content: '',
        auditAnalysis: '',
        memberContent: '',
        source: '',
        keypoints: []
      };

      const typeEl = sol.querySelector('.essay-ques-type');
      question.type = typeEl ? typeEl.textContent.trim() : '';

      const contentEl = sol.querySelector('.question-content');
      if (contentEl) {
        question.content = contentEl.innerText.trim();
      }

      // 粉笔审题
      const auditItems = sol.querySelectorAll('.solu-detail-item');
      auditItems.forEach(item => {
        const headerEl = item.querySelector('h4');
        const headerText = headerEl ? headerEl.textContent.trim() : '';
        const contentDiv = item.querySelector('div > div');
        const contentText = contentDiv ? contentDiv.innerText.trim() : '';

        if (headerText === '粉笔审题') {
          question.auditAnalysis = contentText;
        }
      });

      // 会员专享
      const memberSection = sol.querySelector('app-member-solution-accessory');
      if (memberSection) {
        const memberItems = memberSection.querySelectorAll('.solu-detail-item');
        const memberParts = [];
        memberItems.forEach(item => {
          const headerEl = item.querySelector('h4');
          const headerText = headerEl ? headerEl.textContent.trim() : '';
          const swBg = item.querySelector('.swBg-container');
          if (swBg) {
            memberParts.push(`${headerText}：[会员专享-未解锁]`);
          } else {
            const contentDiv = item.querySelector('div > div');
            const contentText = contentDiv ? contentDiv.innerText.trim() : '';
            memberParts.push(`${headerText}：${contentText}`);
          }
        });
        question.memberContent = memberParts.join('\n\n');
      }

      // 来源
      auditItems.forEach(item => {
        const headerEl = item.querySelector('h4');
        const headerText = headerEl ? headerEl.textContent.trim() : '';
        if (headerText === '来源') {
          const contentDiv = item.querySelector('div > div');
          question.source = contentDiv ? contentDiv.innerText.trim() : '';
        }
      });

      // 考点
      const keypointBtns = sol.querySelectorAll('.keypoint-btn');
      keypointBtns.forEach(btn => {
        question.keypoints.push(btn.textContent.trim());
      });

      questions.push(question);
    });

    log(`${paper.title}：${questions.length}题`, true);

    return {
      paperTitle: paper.title,
      paperNum: paper.paperNum,
      difficulty: paper.difficulty,
      questions: questions
    };
  }

  // ============ 返回列表页 ============
  async function goBackToList() {
    const quitBtn = document.querySelector('.quit-btn');
    if (quitBtn) {
      await humanClick(quitBtn);
      await randomDelay(2500, 4500);
      return true;
    }
    history.back();
    await randomDelay(2500, 4500);
    return true;
  }

  // ============ 主流程 ============
  console.log('===== 粉笔结构化真题抓取 v2（反检测版）=====');
  console.log('特性：随机延迟·模拟人类点击·断点续抓·异常检测');

  // 加载断点
  const progress = loadProgress();
  if (progress.completedPapers.length > 0) {
    console.log(`检测到断点：已完成 ${progress.completedPapers.length} 套试卷，将继续抓取剩余部分`);
    console.log('已完成：' + progress.completedPapers.join(', '));
  }

  // 1. 收集试卷列表
  console.log('\n===== 第一步：收集试卷列表 =====');
  const papers = await collectAllPapers();
  console.log(`共 ${papers.length} 套试卷`);

  if (!papers.length) {
    console.log('未找到试卷，请确保在列表页');
    return;
  }

  // 保存全部试卷标题（断点用）
  progress.allPaperTitles = papers.map(p => p.title);
  saveProgress(progress);

  // 2. 逐个抓取（跳过已完成的）
  console.log('\n===== 第二步：逐个抓取 =====');
  let results = progress.results || [];
  let count = 0;
  let total = papers.length;

  for (let i = 0; i < papers.length; i++) {
    const paper = papers[i];

    // 跳过已完成
    if (progress.completedPapers.includes(paper.title)) {
      log(`跳过已完成：${paper.title}`);
      continue;
    }

    count++;
    console.log(`\n[${progress.completedPapers.length + 1}/${total}] ${paper.title}`);

    // 每抓3套，随机长停顿（模拟人走开休息）
    if (count > 1 && count % 3 === 0) {
      const pauseTime = 5 + Math.random() * 10;
      console.log(`休息 ${pauseTime.toFixed(1)} 秒...`);
      await randomDelay(pauseTime * 1000, pauseTime * 1000 + 2000);
    }

    const result = await extractQuestionsFromPaper(paper);

    if (result) {
      results.push(result);
      progress.completedPapers.push(paper.title);
      progress.results = results;
      saveProgress(progress);
      log(`已保存进度（${progress.completedPapers.length}/${total}）`, true);
    }

    // 检测异常
    if (checkBlocked()) {
      console.log('⚠️ 检测到拦截，脚本暂停。');
      console.log('请手动处理（关闭验证/等待几分钟），然后重新运行脚本。');
      console.log('已完成的进度已保存，重新运行会从断点继续。');
      return;
    }

    // 返回列表页
    await goBackToList();

    // 刷新 DOM 引用
    const refreshedPapers = collectPapersFromCurrentPage();
    for (let j = i + 1; j < papers.length; j++) {
      const refreshed = refreshedPapers.find(p => p.title === papers[j].title);
      if (refreshed) {
        papers[j].element = refreshed.element;
      }
    }

    // 返回后随机停顿
    await randomDelay(1500, 3500);
  }

  // 3. 输出结果
  console.log('\n===== 抓取完成 =====');
  const totalQuestions = results.reduce((sum, r) => sum + r.questions.length, 0);
  console.log(`共 ${results.length} 套试卷，${totalQuestions} 道题`);

  // 统计
  let unlocked = 0, locked = 0;
  results.forEach(r => {
    r.questions.forEach(q => {
      if (q.memberContent.includes('[会员专享-未解锁]')) locked++;
      else if (q.memberContent) unlocked++;
    });
  });
  console.log(`会员内容：已解锁 ${unlocked}，未解锁 ${locked}`);

  const json = JSON.stringify(results, null, 2);

  // 复制到剪贴板
  try {
    await navigator.clipboard.writeText(json);
    console.log('✅ JSON 已复制到剪贴板');
  } catch (e) {
    console.log('⚠️ 剪贴板复制失败');
  }

  // 存 localStorage
  localStorage.setItem(OUTPUT_KEY, json);

  // 下载文件
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `fenbi_结构化真题_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  console.log('✅ JSON 文件已下载');

  // 清除断点
  localStorage.removeItem(PROGRESS_KEY);
  console.log('✅ 断点进度已清除');

  // 输出完整JSON（较长，建议用下载的文件）
  console.log('\n--- JSON 预览（前500字符）---');
  console.log(json.substring(0, 500) + '...');

  return results;
})();
