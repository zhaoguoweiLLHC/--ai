/**
 * 粉笔结构化真题批量抓取脚本
 * 
 * 使用方法：
 * 1. 打开粉笔题库结构化列表页（如 https://www.fenbi.com/tiku/... 2025下分类页）
 * 2. 按 F12 打开开发者工具，切到 Console
 * 3. 粘贴此脚本，回车运行
 * 4. 脚本会自动翻页 + 逐个打开试卷详情页提取题目
 * 5. 完成后在控制台输出 JSON，自动复制到剪贴板
 * 
 * 注意：需要已登录粉笔账号，会员专享内容取决于账号权限
 */

(async function () {
  'use strict';

  // ============ 配置 ============
  const DELAY = 2000;        // 每次操作间隔(ms)
  const OUTPUT_KEY = 'fenbi_questions_result';

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // ============ 第一步：收集所有试卷链接 ============
  async function collectPapers() {
    const papers = [];
    let pageNum = 1;

    while (true) {
      console.log(`[收集试卷] 第${pageNum}页...`);

      // 从DOM提取当前页的试卷项
      const items = document.querySelectorAll('app-paper-item');
      if (!items.length) {
        console.log('[收集试卷] 当前页无试卷项，结束');
        break;
      }

      items.forEach(item => {
        const titleEl = item.querySelector('.item-info-title');
        if (!titleEl) return;
        const title = titleEl.textContent.trim();
        // 提取试卷号
        const match = title.match(/试卷(\d+)/);
        const paperNum = match ? parseInt(match[1]) : null;

        // 获取难度
        const subtitleEl = item.querySelector('.item-info-subtitle');
        const difficulty = subtitleEl ? subtitleEl.textContent.trim() : '';

        // paper-item 是可点击的，但没有直接的 href
        // 我们需要记录 DOM 引用以便后续点击
        papers.push({
          title: title,
          paperNum: paperNum,
          difficulty: difficulty,
          element: item  // 保存DOM引用
        });
      });

      // 尝试翻到下一页
      const pager = document.querySelector('fb-pager');
      if (!pager) {
        console.log('[收集试卷] 无分页器，单页结束');
        break;
      }

      const items2 = pager.querySelectorAll('.item');
      const nextBtn = items2[items2.length - 1]; // 最后一个是"下一页"箭头
      const activePage = pager.querySelector('.active');
      const currentPageNum = activePage ? parseInt(activePage.textContent.trim()) : 1;

      // 检查是否还有下一页
      const allPageNums = Array.from(pager.querySelectorAll('.item')).map(el => {
        const t = el.textContent.trim();
        return /^\d+$/.test(t) ? parseInt(t) : null;
      }).filter(n => n !== null);
      const maxPage = Math.max(...allPageNums, currentPageNum);

      if (currentPageNum >= maxPage) {
        console.log(`[收集试卷] 已到第${currentPageNum}页(共${maxPage}页)，收集完毕`);
        break;
      }

      // 点击下一页
      if (nextBtn) {
        console.log(`[收集试卷] 翻到第${currentPageNum + 1}页...`);
        nextBtn.click();
        await sleep(DELAY);

        // 翻页后DOM引用失效，需要重新收集剩余页
        // 递归收集下一页
        const morePapers = await collectPapersFromCurrentPage();
        // 去重（可能翻页后旧数据还在）
        morePapers.forEach(p => {
          if (!papers.find(existing => existing.title === p.title)) {
            papers.push(p);
          }
        });

        // 检查翻页后的页码是否变了
        const newActive = document.querySelector('fb-pager .active');
        const newPageNum = newActive ? parseInt(newActive.textContent.trim()) : currentPageNum;
        if (newPageNum <= currentPageNum) {
          console.log('[收集试卷] 翻页未生效，结束');
          break;
        }

        if (newPageNum >= maxPage) {
          console.log(`[收集试卷] 已到最后一页，收集完毕`);
          break;
        }
      } else {
        console.log('[收集试卷] 无下一页按钮，结束');
        break;
      }

      pageNum++;
      if (pageNum > 20) {
        console.log('[收集试卷] 安全限制：超过20页，停止');
        break;
      }
    }

    return papers;
  }

  // 从当前页DOM提取试卷（翻页后调用）
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

  // ============ 第二步：逐个打开试卷详情，提取题目 ============
  async function extractQuestionsFromPaper(paper) {
    console.log(`[抓取] 正在打开：${paper.title}...`);

    // 点击试卷项进入详情
    if (paper.element && paper.element.isConnected) {
      paper.element.click();
    } else {
      console.log(`[抓取] DOM引用失效，跳过 ${paper.title}`);
      return null;
    }

    await sleep(DELAY);

    // 等待题目渲染
    let retries = 0;
    while (retries < 5) {
      const solutions = document.querySelectorAll('app-fb-solution');
      if (solutions.length > 0) break;
      retries++;
      console.log(`[抓取] 等待题目渲染...(${retries}/5)`);
      await sleep(1000);
    }

    // 提取题目
    const questions = [];
    const solutionItems = document.querySelectorAll('app-fb-solution');

    solutionItems.forEach((sol, index) => {
      const question = {
        index: index + 1,
        type: '',
        content: '',
        auditAnalysis: '',    // 粉笔审题
        memberContent: '',     // 会员专享内容（考察能力+思维+示例）
        source: '',
        keypoints: []
      };

      // 题型
      const typeEl = sol.querySelector('.essay-ques-type');
      question.type = typeEl ? typeEl.textContent.trim() : '';

      // 题干
      const contentEl = sol.querySelector('.question-content');
      if (contentEl) {
        question.content = contentEl.innerText.trim();
      }

      // 粉笔审题（免费可见）
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

      // 会员专享内容（考察能力与重点 / 粉笔思维 / 粉笔示例）
      const memberSection = sol.querySelector('app-member-solution-accessory');
      if (memberSection) {
        const memberItems = memberSection.querySelectorAll('.solu-detail-item');
        const memberParts = [];
        memberItems.forEach(item => {
          const headerEl = item.querySelector('h4');
          const headerText = headerEl ? headerEl.textContent.trim() : '';
          // 检查是否被遮挡（swBg-container 覆盖了内容）
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
      const sourceItems = sol.querySelectorAll('.solu-detail-item');
      sourceItems.forEach(item => {
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

    console.log(`[抓取] ${paper.title}：提取到 ${questions.length} 道题`);

    return {
      paperTitle: paper.title,
      paperNum: paper.paperNum,
      difficulty: paper.difficulty,
      questions: questions
    };
  }

  // ============ 第三步：返回列表页 ============
  async function goBackToList() {
    // 粉笔详情页有"退出"按钮
    const quitBtn = document.querySelector('.quit-btn');
    if (quitBtn) {
      quitBtn.click();
      console.log('[导航] 返回列表页...');
      await sleep(DELAY);
      return true;
    }

    // 备用：浏览器后退
    history.back();
    await sleep(DELAY);
    return true;
  }

  // ============ 主流程 ============
  console.log('===== 粉笔结构化真题抓取脚本启动 =====');
  console.log('请确保当前在试卷列表页（显示"结构化试卷XX"的页面）');
  console.log('脚本将自动翻页收集所有试卷，然后逐个打开提取题目...\n');

  // 1. 收集所有试卷
  console.log('===== 第一步：收集试卷列表 =====');
  const papers = await collectPapers();
  console.log(`共收集到 ${papers.length} 套试卷：`);
  papers.forEach(p => console.log(`  - ${p.title} (${p.difficulty})`));

  if (!papers.length) {
    console.log('未找到任何试卷，请确保在正确的列表页');
    return;
  }

  // 2. 逐个抓取
  console.log('\n===== 第二步：逐个抓取题目 =====');
  const results = [];

  for (let i = 0; i < papers.length; i++) {
    const paper = papers[i];
    console.log(`\n[${i + 1}/${papers.length}] 处理 ${paper.title}...`);

    const result = await extractQuestionsFromPaper(paper);
    if (result) {
      results.push(result);
    }

    // 返回列表页
    await goBackToList();

    // 重新获取 DOM 引用（返回后页面重新渲染了）
    const refreshedPapers = collectPapersFromCurrentPage();
    for (let j = i + 1; j < papers.length; j++) {
      const refreshed = refreshedPapers.find(p => p.title === papers[j].title);
      if (refreshed) {
        papers[j].element = refreshed.element;
      }
    }

    await sleep(500);
  }

  // 3. 输出结果
  console.log('\n===== 抓取完成 =====');
  console.log(`共抓取 ${results.length} 套试卷，${results.reduce((sum, r) => sum + r.questions.length, 0)} 道题`);

  // 统计会员内容解锁情况
  let unlocked = 0, locked = 0;
  results.forEach(r => {
    r.questions.forEach(q => {
      if (q.memberContent.includes('[会员专享-未解锁]')) {
        locked++;
      } else if (q.memberContent) {
        unlocked++;
      }
    });
  });
  console.log(`会员内容：已解锁 ${unlocked} 题，未解锁 ${locked} 题`);

  // 输出JSON
  const json = JSON.stringify(results, null, 2);
  console.log('\n===== JSON 结果（已复制到剪贴板）=====');

  // 尝试复制到剪贴板
  try {
    await navigator.clipboard.writeText(json);
    console.log('✅ JSON 已复制到剪贴板！可直接粘贴到文件中。');
  } catch (e) {
    console.log('⚠️ 剪贴板复制失败，请手动复制下方JSON：');
  }

  // 同时存到 localStorage 备用
  localStorage.setItem(OUTPUT_KEY, json);
  console.log('✅ JSON 已存到 localStorage（key: ' + OUTPUT_KEY + '）');

  // 输出完整JSON
  console.log(json);

  // 同时提供一个下载链接
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `fenbi_结构化真题_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  console.log('✅ JSON 文件已下载');

  return results;
})();
