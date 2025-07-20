// 全局批量编辑变量，放在 main.js 顶部
let isEditMode = false;
let selectedConversations = new Set();
let currentConversationId = null;

// 知识库编辑模式默认关闭
let kbEditMode = false;
// 声明全局变量 selectedKbFiles
let selectedKbFiles = new Set();

async function renderKnowledgeBase() {
    console.log('调用了 renderKnowledgeBase');
    const knowledgeSection = document.getElementById('knowledge-section');
    knowledgeSection.innerHTML = '';
    try {
        const response = await fetch('/api/knowledge/files');
        if (!response.ok) throw new Error('获取文件列表失败');
        const files = await response.json();
        console.log('files:', files);
        if (!files.length) {
            knowledgeSection.innerHTML = '<div style="color:#718096;text-align:center;padding:20px;">暂无文件</div>';
            return;
        }
        const filesHtml = files.map(file => {
            const fileSize = (file.size / 1024).toFixed(1) + ' KB';
            const isSelected = selectedKbFiles.has(file.name);
            const modified = file.modified ? new Date(file.modified * 1000).toLocaleString('zh-CN', { hour12: false }) : '';
            let iconType = 'alt';
            if (file.type === 'pdf') iconType = 'pdf';
            else if (file.type === 'txt') iconType = 'text';
            else if (file.type === 'md') iconType = 'markdown';
            else if (file.type === 'doc' || file.type === 'docx') iconType = 'word';
            else if (file.type === 'json') iconType = 'code';
            return `
                <div class="kb-file-item sidebar-item" data-filename="${file.name}">
                    ${kbEditMode ? `<input type="checkbox" class="kb-file-checkbox sidebar-checkbox" data-filename="${file.name}" ${isSelected ? 'checked' : ''}>` : ''}
                    <i class="fas fa-file-${iconType} kb-file-icon"></i>
                    <div class="kb-file-info">
                        <span class="kb-file-name" title="${file.name}">${file.name}</span>
                        <div class="kb-file-meta">
                            <span>${fileSize}</span>
                            <span>${modified}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        knowledgeSection.innerHTML = filesHtml;
        if (kbEditMode) {
            document.querySelectorAll('.kb-file-checkbox').forEach(cb => {
                cb.onchange = function() {
                    const filename = this.getAttribute('data-filename');
                    if (this.checked) {
                        selectedKbFiles.add(filename);
                    } else {
                        selectedKbFiles.delete(filename);
                    }
                };
            });
        }
    } catch (error) {
        console.error('渲染知识库文件列表失败:', error);
        knowledgeSection.innerHTML = '<div style=\"color:#f87171;text-align:center;padding:20px;\">加载失败</div>';
    }
}

function cleanWebPageNoise(md) {
    if (!md) return '';
    // 1. 移除所有单独一行的标题（#、##、###等）
    md = md.replace(/^#{1,6} .+$/gm, '');
    // 2. 移除常见栏目/导航/广告等短行
    const navWords = [
        '首页', '专题', '百科', '再现历史', '生活', '说剧', '英文版', '历史话题', 'MILITARY TOPIC', '探寻历史风云旧事',
        '人物', '影视', '解梦', '百家姓', '成语', '明星', '历史', '教育', '三国', '新闻', '手机版'
    ];
    navWords.forEach(word => {
        // 移除单独一行的栏目词
        md = md.replace(new RegExp('^' + word + '\\s*$', 'gm'), '');
    });
    // 3. 移除全大写的短行
    md = md.replace(/^[A-Z\\s]{3,30}$/gm, '');
    // 4. 移除"|"分隔的导航行
    md = md.replace(/^[\\w\\u4e00-\\u9fa5\\s\\|]{5,40}$/gm, function(line) {
        // 只保留含有"|"且全为栏目词的行
        if (line.includes('|')) return '';
        return line;
    });
    // 5. 移除多余空行
    md = md.replace(/\\n{2,}/g, '\\n\\n');
    // 6. 移除开头和结尾的空白
    md = md.trim();
    return md;
}

function cleanMarkdownHeadings(md) {
    return md.replace(/^#{1,2} (.*)$/gm, '### $1');
}
function truncateMarkdownContent(md, maxLen = 400) {
    if (!md) return '';
    if (md.length <= maxLen) return marked.parse(md);
    const short = md.slice(0, maxLen);
    const id = 'expand-' + Math.random().toString(36).slice(2, 10);
    return `
        <div>
            <div id="${id}-short">${marked.parse(short)}<span style="color:#38bdf8;cursor:pointer;" onclick="document.getElementById('${id}-short').style.display='none';document.getElementById('${id}-full').style.display='block';">[展开]</span></div>
            <div id="${id}-full" style="display:none;">${marked.parse(md)}<span style="color:#38bdf8;cursor:pointer;" onclick="document.getElementById('${id}-full').style.display='none';document.getElementById('${id}-short').style.display='block';">[收起]</span></div>
        </div>
    `;
}

function renderConversations() {
    console.log('isEditMode:', isEditMode);
    const conversationsList = document.getElementById('conversations-list');
    if (!conversationsList) {
        console.warn('conversations-list 元素不存在');
        return;
    }
    conversationsList.innerHTML = '';
    if (!conversations || conversations.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'empty-message';
        emptyMessage.textContent = '暂无对话记录';
        conversationsList.appendChild(emptyMessage);
        return;
    }
    conversations.forEach(conv => {
        const conversationItem = document.createElement('div');
        conversationItem.className = 'conversation-item';
        conversationItem.dataset.id = conv.id;
        // 编辑模式下渲染复选框
        let checkbox = null;
        if (isEditMode) {
            checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'conversation-select-checkbox';
            checkbox.setAttribute('data-id', conv.id);
            checkbox.style.marginRight = '10px';
            checkbox.checked = selectedConversations.has(String(conv.id));
            checkbox.onchange = function(e) { e.stopPropagation(); };
            checkbox.onchange = function() {
                if (this.checked) {
                    selectedConversations.add(String(conv.id));
                } else {
                    selectedConversations.delete(String(conv.id));
                }
            };
            conversationItem.appendChild(checkbox);
            // 编辑模式下点击对话项切换勾选
            conversationItem.onclick = (e) => {
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.onchange();
                }
            };
        } else {
            // 非编辑模式下点击切换会话
            conversationItem.onclick = () => {
                if (typeof chatState !== 'undefined' && chatState.isActive) {
                    const tip = document.getElementById('history-switch-tip');
                    if (tip) {
                        if (!tip._showing) {
                            tip.textContent = '对话进行中，无法切换历史记录！';
                            tip._showing = true;
                            setTimeout(() => {
                                tip.textContent = '';
                                tip._showing = false;
                            }, 2000);
                        }
                    }
                    return;
                }
                switchConversation(conv.id);
            };
        }
        const title = document.createElement('div');
        title.className = 'conversation-title';
        title.textContent = conv.title || '新对话';
        const time = document.createElement('div');
        time.className = 'conversation-time';
        time.textContent = new Date(conv.created_at).toLocaleString();
        conversationItem.appendChild(title);
        conversationItem.appendChild(time);
        conversationsList.appendChild(conversationItem);
    });
}

async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        if (!response.ok) {
            throw new Error('获取对话列表失败');
        }
        const data = await response.json();
        conversations = data;
        renderConversations();
    } catch (error) {
        console.error('加载对话列表失败:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const askButton = document.getElementById('ask-button');
    const questionInput = document.getElementById('question-input');
    const progressBar = document.getElementById('progress-bar');
    const steps = document.querySelectorAll('.step');
    const contents = document.querySelectorAll('.progress-content');
    const resultPlaceholder = document.getElementById('result-placeholder');
    const resultContent = document.getElementById('result-content');
    const enableWebSearch = document.getElementById('enable-web-search');
    const maxIterations = document.getElementById('max-iterations');
    const searchMode = document.getElementById('search-mode');

    let progressMessages = [null, '', '', '', '']; // 0号不用，1-4号分别对应四个阶段
    let maxStepReached = 0; // 0=未开始，1=问题接收，2=检索，3=处理，4=生成
    let currentStep = 0; // 当前处于哪个阶段，初始为0
    let finalAnswer = '';
    let lastQuestion = '';
    let lastAnswer = '';
    let lastCreatedAt = '';

    // 页面初始化时，所有步骤都不是active
    steps.forEach((s, i) => {
        s.classList.remove('active', 'completed');
    });
    contents.forEach((c, idx) => {
        c.classList.remove('active');
    });
    progressBar.style.width = '0%';

    // 步骤按钮点击事件
    steps.forEach(step => {
        step.addEventListener('click', function() {
            const stepId = this.id;
            const stepNumber = parseInt(stepId.split('-')[1]);
            if (stepNumber <= maxStepReached && maxStepReached > 0) {
                showStepContent(stepNumber);
                // 新增：切换到Step 3或分析结果区时自动回显答案
                if (stepNumber === 3) {
                    const answerSection = document.querySelector('.answer-section');
                    if (answerSection) answerSection.innerHTML = `<p>${finalAnswer}</p>`;
                }
            }
        });
    });

    function updateProgress(step, message) {
        currentStep = step;
        if (step > maxStepReached) maxStepReached = step;
        progressBar.style.width = `${step * 25}%`;

        steps.forEach((s, i) => {
            if (i < step - 1) {
                s.classList.add('completed');
                s.classList.remove('active');
            } else if (i === step - 1) {
                s.classList.add('active');
                s.classList.remove('completed');
            } else {
                s.classList.remove('active', 'completed');
            }
        });

        contents.forEach((c, idx) => {
            c.classList.remove('active');
            if (idx === step - 1) {
                c.classList.add('active');
                c.querySelector('.content-body').innerHTML = message;
            } else if (progressMessages[idx + 1]) {
                c.querySelector('.content-body').innerHTML = progressMessages[idx + 1];
            }
        });
    }

    function showStepContent(stepNumber) {
        steps.forEach((step, index) => {
            if (index === stepNumber - 1) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
            if (index < stepNumber - 1) {
                step.classList.add('completed');
            } else {
                step.classList.remove('completed');
            }
        });
        contents.forEach((content, idx) => {
            content.classList.remove('active');
            if (idx === stepNumber - 1) {
                content.classList.add('active');
            }
        });
        progressBar.style.width = `${stepNumber * 25}%`;
    }

    async function processQuestion(question) {
        try {
            // Step 1: 问题接收
            progressMessages[1] = `已接收到您的问题：<br><b>${question}</b><br>正在开始处理...`;
            updateProgress(1, progressMessages[1]);
            maxStepReached = 1;

            // Step 2: 文档检索
            const customUrl = document.getElementById('custom-url-input').value.trim();
            const searchMode = document.getElementById('search-mode').value;
            const retrievalResponse = await fetch('/api/retrieve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question,
                    enable_web_search: enableWebSearch.checked,
                    max_iterations: parseInt(maxIterations.value),
                    custom_url: customUrl,
                    search_mode: searchMode
                })
            });
            if (!retrievalResponse.ok) throw new Error('检索失败');
            const contexts = await retrievalResponse.json();
            let retrievalContent = "检索到的相关内容：<br><br>";
            contexts.forEach((ctx, idx) => {
                // 判断类型
                let typeLabel = '';
                if (ctx.type === '指定网页') {
                    typeLabel = `<span style="color:#38bdf8;font-weight:bold;">【指定网页】</span> `;
                } else if (ctx.type === '网络来源') {
                    typeLabel = `<span style="color:#4ade80;">【联网检索】</span> `;
                } else {
                    typeLabel = `<span style="color:#fbbf24;">【本地文档】</span> `;
                }
                // 标题优先显示
                let title = ctx.title ? `<b>${ctx.title}</b> ` : '';
                // url显示（仅指定网页/网络来源）
                let url = (ctx.type === '指定网页' || ctx.type === '网络来源') && ctx.url
                    ? `<a href="${ctx.url}" target="_blank" style="color:#38bdf8;text-decoration:underline;">${ctx.url}</a><br>`
                    : '';
                let contentHtml;
                if (ctx.type === '指定网页') {
                    let cleaned = cleanWebPageNoise(ctx.content || '');
                    cleaned = cleanMarkdownHeadings(cleaned);
                    contentHtml = truncateMarkdownContent(cleaned, 400);
                } else {
                    contentHtml = marked.parse(ctx.content ? ctx.content.substring(0, 200) : '');
                }
                retrievalContent += `${idx + 1}. ${typeLabel}${title}${url}${contentHtml}<br><br>`;
            });
            progressMessages[2] = retrievalContent;
            updateProgress(2, progressMessages[2]);
            maxStepReached = 2;

            await new Promise(resolve => setTimeout(resolve, 2000));

            // Step 3: 生成答案（流式输出）
            progressMessages[3] = `<b>生成的答案：</b><br><span id='streaming-answer'></span>`;
            updateProgress(3, progressMessages[3]);
            maxStepReached = 3;

            // 流式fetch大模型答案
            const response = await fetch('/api/generate_stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, contexts })
            });
            const reader = response.body.getReader();
            let decoder = new TextDecoder();
            let resultText = '';
            let streamingAnswer = document.getElementById('streaming-answer');
            const answerSection = document.querySelector('.answer-section');
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                resultText += chunk;
                if (streamingAnswer) streamingAnswer.innerHTML = marked.parse(resultText);
                if (answerSection) answerSection.innerHTML = marked.parse(resultText);
            }
            finalAnswer = resultText;
            // 保证Step 3进度内容和分析结果区都能显示完整答案
            progressMessages[3] = `<b>生成的答案：</b><br>${marked.parse(finalAnswer)}`;
            updateProgress(3, progressMessages[3]);
            if (answerSection) answerSection.innerHTML = marked.parse(finalAnswer);

            // Step 3流式输出完毕后，自动跳转到Step 4，流式fetch冲突检测
            progressMessages[4] = `<b>冲突检测总结：</b><br><span id='streaming-conflict'>正在等待冲突检测结果...<span class='loading-dots'></span></span>`;
            updateProgress(4, progressMessages[4]);
            maxStepReached = 4;

            const conflictResponse = await fetch('/api/conflict_stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contexts })
            });
            const conflictReader = conflictResponse.body.getReader();
            let conflictDecoder = new TextDecoder();
            let conflictText = '';
            let streamingConflict = document.getElementById('streaming-conflict');
            let firstChunk = true;

            try {
                while (true) {
                    const { done, value } = await conflictReader.read();
                    if (done) break;
                    const chunk = conflictDecoder.decode(value, { stream: true });
                    conflictText += chunk;
                    if (streamingConflict) {
                        if (firstChunk) {
                            streamingConflict.innerHTML = '';
                            firstChunk = false;
                        }
                        streamingConflict.innerHTML = marked.parse(conflictText);
                    }
                }
            } catch (e) {
                console.error('冲突检测流式输出错误:', e);
                if (streamingConflict) {
                    streamingConflict.innerHTML = '<span style="color:#fbbf24;">⚠️ 冲突检测过程中出现错误，但不会影响最终答案的生成。</span>';
                }
                conflictText = '冲突检测过程中出现错误，但不会影响最终答案的生成。';
            }

            // 确保streamingConflict有内容
            if (streamingConflict && (!conflictText || conflictText.trim() === '')) {
                streamingConflict.innerHTML = '<span style="color:#38bdf8;">未检测到明显冲突。</span>';
                conflictText = '未检测到明显冲突。';
            }

            // 冲突检测流式输出完毕后，返回完整结果对象
            const result = {
                answer: finalAnswer,
                sources: contexts,
                hasConflicts: /有冲突/.test(conflictText),
                conflict_reason: conflictText,
                injected_prompt: '', // 如需可补充
            };
            // 保证sources为扁平数组
            if (!result || !Array.isArray(result.sources)) {
                result.sources = [];
            } else if (Array.isArray(result.sources[0])) {
                result.sources = result.sources.flat();
            }
            result.sources = result.sources.filter(item => item && typeof item === 'object');
            return result;
        } catch (error) {
            throw error;
        }
    }

    function displayResult(result) {
        try {
            console.log('displayResult收到的result:', result);
            if (!result || !Array.isArray(result.sources)) {
                result.sources = [];
            } else if (Array.isArray(result.sources[0])) {
                result.sources = result.sources.flat();
            }
            result.sources = result.sources.filter(item => item && typeof item === 'object');
            resultPlaceholder.style.display = 'none';
            resultContent.style.display = 'block';

            // 折叠上一次结果到历史区
            if (lastQuestion && lastAnswer) {
                const historySection = document.getElementById('history-section');
                const historyId = 'history-local-' + Date.now();
                let createdAt = '';
                if (lastCreatedAt) {
                    const dateObj = new Date(lastCreatedAt.replace(' ', 'T').replace(/-/g, '/'));
                    createdAt = dateObj.toLocaleString('zh-CN', { hour12: false });
                    if (createdAt.startsWith('时间：')) {
                        createdAt = createdAt.replace(/^时间：/, '');
                    }
                }
                const html = `
                    <div class="history-item" style="margin-bottom:8px;">
                        <div class="history-header" style="cursor:pointer;background:#22344a;padding:10px;border-radius:6px;" onclick="const b=document.getElementById('${historyId}-body');b.style.display=b.style.display==='none'?'block':'none'">
                            <b>历史提问：</b> ${lastQuestion.replace(/</g,'&lt;').replace(/>/g,'&gt;').slice(0,60)} <span style="color:#38bdf8;">[点击展开/收起]</span>
                        </div>
                        <div class="history-body" id="${historyId}-body" style="display:none;background:#1a2533;padding:12px;border-radius:6px;">
                            <b>问题：</b> ${lastQuestion.replace(/</g,'&lt;').replace(/>/g,'&gt;')}<br><b>答案：</b><br>${marked.parse(lastAnswer||'')}
                            <div style="color:#888;font-size:0.92em;margin-top:6px;">${createdAt ? '时间：' + createdAt : ''}</div>
                        </div>
                    </div>
                `;
                historySection.insertAdjacentHTML('afterbegin', html);
            }
            // 记录本次问题和答案
            lastQuestion = '';
            lastAnswer = '';
            if (
                result.sources &&
                result.sources.length &&
                typeof result.sources[0] === 'object' &&
                result.sources[0] !== null &&
                'question' in result.sources[0]
            ) {
                lastQuestion = result.sources[0].question;
            } else if (window.currentQuestion) {
                lastQuestion = window.currentQuestion;
            }
            lastAnswer = result.answer || '';
            lastCreatedAt = result.created_at;

            // Display answer
            const answerSection = resultContent.querySelector('.answer-section');
            answerSection.innerHTML = marked.parse(result.answer || '');

            // Display sources
            const sourcesList = resultContent.querySelector('.sources-list');
            sourcesList.innerHTML = '';
            (result.sources || []).forEach(source => {
                const sourceElement = document.createElement('div');
                sourceElement.className = 'source-item';

                let typeLabel = '';
                let icon = '';
                let urlHtml = '';
                let title = source.title ? `<b>${source.title}</b><br>` : '';

                if (source.type === '指定网页') {
                    typeLabel = `<span style="color:#38bdf8;font-weight:bold;">🌐 指定网页</span>`;
                    icon = '🌐';
                    if (source.url) {
                        urlHtml = `<div style="margin-top:4px;"><a href="${source.url}" target="_blank" style="color:#38bdf8;text-decoration:underline;">${source.url}</a></div>`;
                    }
                } else if (source.type === '网络来源') {
                    typeLabel = `<span style="color:#4ade80;">🌐 联网检索</span>`;
                    icon = '🌐';
                    if (source.url) {
                        urlHtml = `<div style="margin-top:4px;"><a href="${source.url}" target="_blank" style="color:#38bdf8;text-decoration:underline;">${source.url}</a></div>`;
                    }
                } else {
                    typeLabel = `<span style="color:#fbbf24;">📄 本地文档</span>`;
                    icon = '📄';
                }

                let contentHtml;
                if (source.type === '指定网页') {
                    let cleaned = cleanWebPageNoise(source.content || '');
                    cleaned = cleanMarkdownHeadings(cleaned);
                    contentHtml = truncateMarkdownContent(cleaned, 400);
                } else {
                    contentHtml = marked.parse(source.content || '');
                }
                sourceElement.innerHTML = `
                    <div class="source-type">${typeLabel}</div>
                    <div class="source-content">
                        ${title}
                        ${contentHtml}
                        ${urlHtml}
                    </div>
                `;
                sourcesList.appendChild(sourceElement);
            });

            // Display conflict warning if needed
            if (result.hasConflicts) {
                const warningElement = document.createElement('div');
                warningElement.className = 'conflict-warning';
                warningElement.innerHTML = `
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>检测到不同来源的信息存在潜在冲突，请注意甄别。</p>
                    <div style='margin-top:8px; color:#fbbf24; font-size:0.98rem;'><b>冲突检测推理过程：</b><br>${marked.parse(result.conflict_reason || '')}</div>
                `;
                resultContent.appendChild(warningElement);
            }
        } catch (e) {
            console.error('分析结果渲染异常:', e, result);
            alert('分析结果渲染异常，请刷新页面重试\n' + e.message);
        }
    }

    // 在历史区上方添加编辑和多选操作区
    const historySection = document.getElementById('history-section');
    let editMode = false;
    let selectedIds = [];

    function setEditMode(on) {
        editMode = on;
        renderHistoryControls();
        document.querySelectorAll('.history-item').forEach(item => {
            const id = item.getAttribute('data-id');
            let header = item.querySelector('.history-header');
            if (on) {
                if (!header.querySelector('.history-select-checkbox')) {
                    const cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.className = 'history-select-checkbox';
                    cb.setAttribute('data-id', id);
                    cb.style = 'margin-right:10px;vertical-align:middle;';
                    cb.checked = selectedIds.includes(id);
                    cb.onclick = function(e) { e.stopPropagation(); };
                    cb.onchange = function() {
                        if (cb.checked) {
                            if (!selectedIds.includes(id)) selectedIds.push(id);
                        } else {
                            selectedIds = selectedIds.filter(x => x !== id);
                        }
                    };
                    header.insertBefore(cb, header.firstChild);
                }
            } else {
                const cb = header.querySelector('.history-select-checkbox');
                if (cb) header.removeChild(cb);
            }
        });
    }

    // 历史记录批量编辑与删除
    let historyEditMode = false;
    let selectedHistoryIds = new Set();

    function renderHistoryControls() {
        let historySection = document.getElementById('history-section');
        if (!historySection) {
            console.warn('history-section 元素不存在');
            return;
        }
        if (!historySection.parentNode) {
            console.warn('history-section.parentNode 不存在，无法插入 controlsDiv');
            return;
        }
        let controlsDiv = document.getElementById('history-controls');
        if (!controlsDiv) {
            controlsDiv = document.createElement('div');
            controlsDiv.id = 'history-controls';
            controlsDiv.style = 'margin-bottom:8px;';
            historySection.parentNode.insertBefore(controlsDiv, historySection);
        }
        let controlsHtml = '';
        if (!historyEditMode) {
            controlsHtml = `<button id="edit-history-btn" class="tab-btn" style="margin-bottom:10px;">编辑</button>`;
        } else {
            controlsHtml = `
                <button id="select-all-history-btn" class="tab-btn" style="margin-bottom:10px;">全选</button>
                <button id="delete-selected-history-btn" class="tab-btn" style="background:#f87171;color:#fff;margin-bottom:10px;">批量删除</button>
                <button id="cancel-history-edit-btn" class="tab-btn" style="background:#22344a;color:#aaa;margin-bottom:10px;">取消</button>
            `;
        }
        controlsDiv.innerHTML = controlsHtml;

        // 事件绑定
        safeAddEventListener('edit-history-btn', 'click', () => {
            historyEditMode = true;
            selectedHistoryIds.clear();
            renderHistory();
        });
        safeAddEventListener('cancel-history-edit-btn', 'click', () => {
            historyEditMode = false;
            selectedHistoryIds.clear();
            renderHistory();
        });
        safeAddEventListener('select-all-history-btn', 'click', () => {
            const checkboxes = document.querySelectorAll('.history-select-checkbox');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            checkboxes.forEach(cb => {
                cb.checked = !allChecked;
                const id = cb.getAttribute('data-id');
                if (!allChecked) {
                    selectedHistoryIds.add(id);
                } else {
                    selectedHistoryIds.delete(id);
                }
            });
        });
        safeAddEventListener('delete-selected-history-btn', 'click', async () => {
            if (!selectedHistoryIds.size) {
                alert('请先选择要删除的历史记录');
                return;
            }
            if (!confirm('确定要删除选中的历史记录吗？')) return;
            for (const id of selectedHistoryIds) {
                try {
                    await fetch(`/api/history/${id}`, { method: 'DELETE' });
                } catch(e) {}
            }
            selectedHistoryIds.clear();
            historyEditMode = false;
            await renderHistory();
        });
    }

    // 修改渲染历史问答函数，支持多选
    async function renderHistory() {
        renderHistoryControls();
        const historySection = document.getElementById('history-section');
        if (!historySection) {
            console.warn('history-section 元素不存在');
            return;
        }
        historySection.innerHTML = '';
        try {
            const resp = await fetch('/api/history');
            if (!resp.ok) return;
            const history = await resp.json();
            if (!history.length) return;
            
            history.forEach((item, idx) => {
                const historyId = 'history-' + item.id;
                let createdAt = '';
                if (item.created_at) {
                    let dateObj = new Date(item.created_at);
                    if (isNaN(dateObj.getTime())) {
                        dateObj = new Date(item.created_at.replace(' ', 'T'));
                    }
                    if (isNaN(dateObj.getTime())) {
                        dateObj = new Date(item.created_at.replace(/-/g, '/'));
                    }
                    if (!isNaN(dateObj.getTime())) {
                        // 手动加8小时，显示北京时间
                        dateObj = new Date(dateObj.getTime() + 8 * 60 * 60 * 1000);
                        createdAt = dateObj.toLocaleString('zh-CN', { hour12: false });
                    }
                }
                if (!createdAt || createdAt === 'Invalid Date') {
                    createdAt = '';
                }
                let checkboxHtml = '';
                if (historyEditMode) {
                    checkboxHtml = `<input type="checkbox" class="history-select-checkbox sidebar-checkbox" data-id="${item.id}" ${selectedHistoryIds.has(String(item.id)) ? 'checked' : ''}>`;
                }
                const html = `
                    <div class="chat-history-item sidebar-item" data-id="${item.id}">
                        <div class="chat-message user">
                            ${checkboxHtml}
                            <div class="message-content">${item.question.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
                            <div class="message-time">${createdAt}</div>
                        </div>
                        <div class="chat-message assistant">
                            <div class="message-content">${marked.parse(item.answer || '')}</div>
                            <div class="message-time">${createdAt}</div>
                        </div>
                    </div>
                `;
                historySection.insertAdjacentHTML('beforeend', html);
            });
            // 新增：为每个历史记录项添加点击事件，只有在对话未激活时才允许切换
            document.querySelectorAll('.chat-history-item').forEach(item => {
                item.onclick = function(e) {
                    if (typeof chatState !== 'undefined' && chatState.isActive) {
                        e.preventDefault();
                        e.stopPropagation();
                        // 只在#history-switch-tip显示提示，且不会刷屏
                        const tip = document.getElementById('history-switch-tip');
                        if (tip) {
                            if (!tip._showing) {
                                tip.textContent = '对话进行中，无法切换历史记录！';
                                tip._showing = true;
                                setTimeout(() => {
                                    tip.textContent = '';
                                    tip._showing = false;
                                }, 2000);
                            }
                        }
                        return false;
                    }
                    // 这里可以放原有的切换逻辑（如有）
                };
            });
            if (historyEditMode) {
                document.querySelectorAll('.history-select-checkbox').forEach(cb => {
                    cb.onchange = function() {
                        const id = this.getAttribute('data-id');
                        if (this.checked) {
                            selectedHistoryIds.add(id);
                        } else {
                            selectedHistoryIds.delete(id);
                        }
                    };
                });
            }
        } catch(e) {
            console.error('加载历史记录失败:', e);
        }
    }

    // 添加对话状态管理
    let chatState = {
        isActive: false,
        messages: [],
        currentQuestion: '',
        contexts: []
    };

    // 修改添加消息到对话界面的函数
    function addChatMessage(role, content) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        messageDiv.style.marginBottom = '10px';
        messageDiv.style.padding = '10px';
        messageDiv.style.borderRadius = '8px';
        messageDiv.style.maxWidth = '80%';
        
        if (role === 'user') {
            messageDiv.style.marginLeft = 'auto';
            messageDiv.style.backgroundColor = 'rgba(58,134,255,0.2)';
        } else if (role === 'assistant') {
            messageDiv.style.marginRight = 'auto';
            messageDiv.style.backgroundColor = 'rgba(42,91,140,0.2)';
        } else {
            messageDiv.style.margin = '5px auto';
            messageDiv.style.backgroundColor = 'rgba(251,191,36,0.2)';
            messageDiv.style.textAlign = 'center';
        }
        
        messageDiv.innerHTML = marked.parse(content);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 修改提问按钮的点击事件处理
    safeAddEventListener('ask-button', 'click', async () => {
        const question = questionInput.value.trim();
        if (!question) return;

        // 如果没有当前对话，创建新对话
        if (!currentConversationId) {
            currentConversationId = 'conv-' + Date.now();
            const newConversation = {
                id: currentConversationId,
                title: question.slice(0, 30) + (question.length > 30 ? '...' : ''),
                created_at: new Date().toISOString()
            };
            // 保存新对话到数据库
            try {
                const response = await fetch('/api/conversations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newConversation)
                });
                if (!response.ok) {
                    throw new Error('创建对话失败');
                }
                // 重新加载对话列表
                await loadConversations();
            } catch (error) {
                console.error('保存对话失败:', error);
                return;
            }
        }

        // 禁用输入和按钮
        questionInput.disabled = true;
        askButton.disabled = true;
        askButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            // 添加用户消息到界面
            addChatMessage('user', question);
            // 用户消息写入数据库
            if (currentConversationId) {
                await fetch(`/api/conversations/${currentConversationId}/messages`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: 'user',
                        content: question
                    })
                });
            }
            // 更新对话状态
            chatState.messages.push({ role: 'user', content: question });

            // 调用大模型判断意图和攻击
            const intentResponse = await fetch('/api/intent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            if (!intentResponse.ok) {
                throw new Error('意图判断失败');
            }
            const intentResult = await intentResponse.json();
            if (intentResult.attack_detected) {
                alert('检测到您的输入可能包含攻击性或越狱内容，请重新输入。');
                questionInput.value = '';
                questionInput.disabled = false;
                askButton.disabled = false;
                askButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
                return;
            }
            // 如果意图是宋代历史信息询问，则继续进入下一阶段
            if (intentResult.intent === 'history_query') {
                // 清空分析结果区
                resultPlaceholder.style.display = 'block';
                resultContent.style.display = 'none';
                const answerSection = document.querySelector('.answer-section');
                if (answerSection) answerSection.innerHTML = '';
                const sourcesList = document.querySelector('.sources-list');
                if (sourcesList) sourcesList.innerHTML = '';
                document.querySelectorAll('.conflict-warning').forEach(el => el.remove());
                // 继续处理检索和生成
                const finalResult = await processQuestion(question);
                // 新增：将检索型答案也插入到对话区
                addChatMessage('assistant', finalResult.answer);
                // AI消息写入数据库
                if (currentConversationId) {
                    await fetch(`/api/conversations/${currentConversationId}/messages`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            role: 'assistant',
                            content: finalResult.answer
                        })
                    });
                }
                displayResult(finalResult);
            } else {
                // 否则直接返回大模型回复
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: question,
                        chat_history: chatState.messages,
                        conversation_id: currentConversationId
                    })
                });
                if (!response.ok) {
                    throw new Error('对话请求失败');
                }
                const result = await response.json();
                // 添加AI回复到界面
                addChatMessage('assistant', result.message);
                // AI消息写入数据库
                if (currentConversationId) {
                    await fetch(`/api/conversations/${currentConversationId}/messages`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            role: 'assistant',
                            content: result.message
                        })
                    });
                }
                // 更新对话状态
                chatState.messages.push({ role: 'assistant', content: result.message });
            }
            // 重置输入框状态
            questionInput.value = '';
            questionInput.disabled = false;
            questionInput.focus();
            askButton.disabled = false;
            askButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } catch (error) {
            console.error('对话失败:', error);
            const errorMessage = '抱歉，对话出现错误，请重试';
            addChatMessage('system', errorMessage);
            questionInput.disabled = false;
            askButton.disabled = false;
            askButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    });

    // 修改切换对话的函数
    async function switchConversation(convId) {
        currentConversationId = convId;
        
        // 从数据库获取对话消息
        try {
            const response = await fetch(`/api/conversations/${convId}/messages`);
            if (!response.ok) {
                throw new Error('获取对话消息失败');
            }
            const messages = await response.json();
            
            // 更新对话状态
            chatState.messages = messages;
            chatState.isActive = true;
            
            // 更新主界面的对话
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = '';
            messages.forEach(msg => {
                addChatMessage(msg.role, msg.content);
            });
            
            // 更新UI
            renderConversations();
        } catch (error) {
            console.error('切换对话失败:', error);
        }
    }
    window.switchConversation = switchConversation;

    // 修改输入框的回车事件
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            askButton.click();
        }
    });

    renderHistory();

    // 知识库管理相关功能

    // setKbEditMode 只在点击编辑按钮时设为 true
    function setKbEditMode(on) {
        kbEditMode = on;
        const editControls = document.getElementById('kb-edit-controls');
        const normalControls = document.getElementById('kb-normal-controls');
        if (editControls && normalControls) {
            editControls.style.display = on ? 'flex' : 'none';
            normalControls.style.display = on ? 'none' : 'block';
        }
        renderKnowledgeBase();
    }

    // 文件上传处理
    document.getElementById('file-upload').addEventListener('change', async function(e) {
        const files = e.target.files;
        if (!files.length) return;

        // 显示 loading
        const kbUploadLoading = document.getElementById('kb-upload-loading');
        if (kbUploadLoading) kbUploadLoading.style.display = 'block';

        const formData = new FormData();
        for (let file of files) {
            formData.append('files[]', file, file.name);
        }

        try {
            const response = await fetch('/api/knowledge/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '上传失败');
            }
            const result = await response.json();
            if (result.error) throw new Error(result.error);
            alert('文件上传成功');
            await renderKnowledgeBase(); // 上传成功后自动刷新文件列表
        } catch (error) {
            console.error('文件上传失败:', error);
            alert('文件上传失败: ' + error.message);
        }
        // 隐藏 loading
        if (kbUploadLoading) kbUploadLoading.style.display = 'none';
        // 清空文件输入
        e.target.value = '';
    });

    // 刷新按钮
    document.getElementById('refresh-kb-btn').onclick = renderKnowledgeBase;

    // 编辑按钮点击事件
    document.getElementById('edit-kb-btn').onclick = () => {
        setKbEditMode(true);
    };

    // 取消编辑按钮点击事件
    document.getElementById('cancel-kb-edit-btn').onclick = () => {
        setKbEditMode(false);
        selectedKbFiles.clear();
    };

    // 全选按钮点击事件
    safeAddEventListener('select-all-btn', 'click', () => {
        if (!isEditMode) return;
        if (selectedConversations.size === conversations.length) {
            // 取消全选
            selectedConversations.clear();
        } else {
            // 全选
            conversations.forEach(conv => selectedConversations.add(String(conv.id)));
        }
        renderConversations();
    });

    // 删除选中按钮点击事件
    safeAddEventListener('delete-selected-btn', 'click', async () => {
        if (!selectedConversations.size) {
            alert('请先选择要删除的对话');
            return;
        }
        if (!confirm(`确定要删除选中的 ${selectedConversations.size} 个对话吗？`)) {
            return;
        }
        try {
            for (const convId of selectedConversations) {
                const resp = await fetch(`/api/conversations/${convId}`, {
                    method: 'DELETE'
                });
                if (!resp.ok) {
                    throw new Error('删除失败');
                }
            }
            if (selectedConversations.has(currentConversationId)) {
                currentConversationId = null;
                chatState.messages = [];
                document.getElementById('chat-messages').innerHTML = '';
            }
            await loadConversations();
            isEditMode = false;
            selectedConversations.clear();
            document.getElementById('batch-actions').style.display = 'none';
            renderConversations();
        } catch (error) {
            console.error('删除对话失败:', error);
            alert('删除对话失败，请重试');
        }
    });
    
    // 添加取消编辑按钮事件监听
    safeAddEventListener('cancel-edit-btn', 'click', () => {
        isEditMode = false;
        selectedConversations.clear();
        document.getElementById('batch-actions').style.display = 'none';
        renderConversations();
    });

    if (typeof renderHistory === 'function') {
        renderHistory();
    }

    // 渲染批量操作按钮区时，先清空再插入，防止重复
    function renderBatchActions() {
        const batchActions = document.getElementById('batch-actions');
        if (batchActions) {
            batchActions.innerHTML = '';
            batchActions.innerHTML = `
                <button id="select-all-btn" class="tab-btn">全选</button>
                <button id="delete-selected-btn" class="tab-btn" style="background:#f87171;color:#fff;">批量删除</button>
                <button id="cancel-edit-btn" class="tab-btn" style="background:#22344a;color:#aaa;">取消</button>
            `;
            // 事件绑定
            safeAddEventListener('select-all-btn', 'click', () => {
                if (!isEditMode) return;
                if (selectedConversations.size === conversations.length) {
                    // 取消全选
                    selectedConversations.clear();
                } else {
                    // 全选
                    conversations.forEach(conv => selectedConversations.add(String(conv.id)));
                }
                renderConversations();
            });
            safeAddEventListener('delete-selected-btn', 'click', async () => {
                if (!selectedConversations.size) {
                    alert('请先选择要删除的对话');
                    return;
                }
                if (!confirm(`确定要删除选中的 ${selectedConversations.size} 个对话吗？`)) {
                    return;
                }
                try {
                    for (const convId of selectedConversations) {
                        const resp = await fetch(`/api/conversations/${convId}`, {
                            method: 'DELETE'
                        });
                        if (!resp.ok) {
                            throw new Error('删除失败');
                        }
                    }
                    if (selectedConversations.has(currentConversationId)) {
                        currentConversationId = null;
                        chatState.messages = [];
                        document.getElementById('chat-messages').innerHTML = '';
                    }
                    await loadConversations();
                    isEditMode = false;
                    selectedConversations.clear();
                    document.getElementById('batch-actions').style.display = 'none';
                    renderConversations();
                } catch (error) {
                    console.error('删除对话失败:', error);
                    alert('删除对话失败，请重试');
                }
            });
            safeAddEventListener('cancel-edit-btn', 'click', () => {
                isEditMode = false;
                selectedConversations.clear();
                document.getElementById('batch-actions').style.display = 'none';
                renderBatchActions();
                renderConversations();
            });
        }
    }
    // 在切换编辑模式时调用 renderBatchActions()
    safeAddEventListener('edit-mode-btn', 'click', () => {
        isEditMode = true;
        selectedConversations.clear();
        document.getElementById('batch-actions').style.display = 'flex';
        renderBatchActions();
        renderConversations();
    });
    safeAddEventListener('cancel-edit-btn', 'click', () => {
        isEditMode = false;
        selectedConversations.clear();
        document.getElementById('batch-actions').style.display = 'none';
        renderBatchActions();
        renderConversations();
    });
    safeAddEventListener('select-all-btn', 'click', () => {
        if (!isEditMode) return;
        if (selectedConversations.size === conversations.length) {
            // 取消全选
            selectedConversations.clear();
        } else {
            // 全选
            conversations.forEach(conv => selectedConversations.add(String(conv.id)));
        }
        renderConversations();
    });
    safeAddEventListener('delete-selected-btn', 'click', async () => {
        if (!selectedConversations.size) {
            alert('请先选择要删除的对话');
            return;
        }
        if (!confirm(`确定要删除选中的 ${selectedConversations.size} 个对话吗？`)) {
            return;
        }
        try {
            for (const convId of selectedConversations) {
                const resp = await fetch(`/api/conversations/${convId}`, {
                    method: 'DELETE'
                });
                if (!resp.ok) {
                    throw new Error('删除失败');
                }
            }
            if (selectedConversations.has(currentConversationId)) {
                currentConversationId = null;
                chatState.messages = [];
                document.getElementById('chat-messages').innerHTML = '';
            }
            await loadConversations();
            isEditMode = false;
            selectedConversations.clear();
            document.getElementById('batch-actions').style.display = 'none';
            renderConversations();
        } catch (error) {
            console.error('删除对话失败:', error);
            alert('删除对话失败，请重试');
        }
    });

    // 新建对话按钮事件绑定
    safeAddEventListener('new-chat-btn', 'click', async () => {
        // 如果当前有对话且未保存，先保存当前对话
        if (currentConversationId && chatState.messages.length > 0) {
            try {
                // 保存当前对话的最后一条消息作为标题
                const lastMessage = chatState.messages[chatState.messages.length - 1];
                const title = lastMessage.content.slice(0, 30) + (lastMessage.content.length > 30 ? '...' : '');
                // 更新对话标题
                await fetch(`/api/conversations/${currentConversationId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title })
                });
                // 重新加载对话列表
                await loadConversations();
            } catch (error) {
                console.error('保存当前对话失败:', error);
            }
        }
        // 清空当前对话状态
        currentConversationId = null;
        chatState.messages = [];
        chatState.isActive = false;
        // 清空对话框
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) chatMessages.innerHTML = '';
        // 清空输入框
        const questionInput = document.getElementById('question-input');
        if (questionInput) questionInput.value = '';
        // 更新UI
        renderConversations();
        // 聚焦到输入框
        if (questionInput) questionInput.focus();
    });

    // 标签页切换按钮事件绑定
    safeAddEventListener('history-tab-btn', 'click', () => {
        switchTab('history');
    });
    safeAddEventListener('knowledge-tab-btn', 'click', () => {
        switchTab('knowledge');
    });

    // 在知识库管理相关功能部分，添加删除选中按钮的事件处理
    safeAddEventListener('delete-selected-kb-btn', 'click', async () => {
        if (!selectedKbFiles.size) {
            alert('请先选择要删除的文件');
            return;
        }
        if (!confirm(`确定要删除选中的 ${selectedKbFiles.size} 个文件吗？`)) {
            return;
        }
        try {
            const response = await fetch('/api/knowledge/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_names: Array.from(selectedKbFiles) })
            });
            if (!response.ok) {
                throw new Error('删除失败');
            }
            selectedKbFiles.clear();
            await renderKnowledgeBase();
        } catch (error) {
            console.error('删除知识库文件失败:', error);
            alert('删除知识库文件失败，请重试');
        }
    });

    // 确保知识库按钮区初始状态正确
    const editControls = document.getElementById('kb-edit-controls');
    const normalControls = document.getElementById('kb-normal-controls');
    if (editControls && normalControls) {
        editControls.style.display = 'none';
        normalControls.style.display = 'block';
    }

    // 侧栏收起/展开
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
    const openSidebarBtn = document.getElementById('open-sidebar-btn');

    if (toggleSidebarBtn && sidebar && openSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function() {
            sidebar.style.display = 'none';
            openSidebarBtn.style.display = 'block';
        });
    }
    if (openSidebarBtn && sidebar) {
        openSidebarBtn.addEventListener('click', function() {
            sidebar.style.display = 'block';
            openSidebarBtn.style.display = 'none';
        });
    }
    // 页面初始时只显示侧栏，隐藏"打开"按钮
    if (sidebar && openSidebarBtn) {
        sidebar.style.display = 'block';
        openSidebarBtn.style.display = 'none';
    }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', async () => {
    const questionInput = document.getElementById('question-input');
    try {
        console.log('页面开始加载...');
        // 初始化对话状态
        chatState = {
            messages: [],
            isActive: false
        };
        // 加载历史对话记录
        console.log('开始获取对话列表...');
        const response = await fetch('/api/conversations');
        console.log('获取到响应:', response.status);
        if (!response.ok) {
            throw new Error('获取对话列表失败');
        }
        conversations = await response.json(); // 赋值全局变量
        console.log('获取到对话列表:', conversations);
        renderConversations(); // 统一渲染
        // 初始化事件监听
        initializeEventListeners();
        // 聚焦到输入框
        questionInput.focus();
        console.log('页面初始化完成');
    } catch (error) {
        console.error('初始化失败:', error);
    }
});

// 初始化事件监听器
function initializeEventListeners() {
    // ... existing code ...
}

// 新增 safeAddEventListener 函数
function safeAddEventListener(id, event, handler) {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener(event, handler);
    } else {
        console.warn(`safeAddEventListener: 元素不存在: ${id}，事件绑定已跳过。`);
    }
}

function switchTab(tabName) {
    const historyTabBtn = document.getElementById('history-tab-btn');
    const knowledgeTabBtn = document.getElementById('knowledge-tab-btn');
    const historyPanel = document.getElementById('history-panel');
    const knowledgePanel = document.getElementById('knowledge-panel');
    // 更新按钮状态
    if (historyTabBtn && knowledgeTabBtn) {
        historyTabBtn.classList.toggle('active', tabName === 'history');
        knowledgeTabBtn.classList.toggle('active', tabName === 'knowledge');
    }
    // 更新面板显示
    if (historyPanel && knowledgePanel) {
        historyPanel.classList.toggle('active', tabName === 'history');
        knowledgePanel.classList.toggle('active', tabName === 'knowledge');
    }
    // 切到知识库时刷新文件列表
    if (tabName === 'knowledge') {
        renderKnowledgeBase();
    }
}