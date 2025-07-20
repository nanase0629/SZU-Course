import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;

public class giveQuestion extends JFrame{
    // 界面组件定义
    private JLabel questionLabel; // 显示问题的标签
    private JRadioButton[] singleChoiceOptions; // 单选题选项
    private JCheckBox[] multipleChoiceOptions; // 多选题选项
    private JRadioButton trueOption, falseOption; // 判断题选项
    private JButton submitButton; // 提交按钮
    private JLabel timeLabel; // 倒计时标签
    private Timer timer; // 倒计时器

    // 问题相关变量
    private int currentQuestionIndex = 0; // 当前问题的索引
    private int totalQuestions = 15; // 总问题数
    private boolean[] answerResults = new boolean[totalQuestions]; // 记录每个问题的答案是否正确

    private JLabel singleNumber; // 单选题数量
    private JLabel MutNumber; // 多选题数量
    private JLabel ValidNumber; // 判断题数量

    private JLabel singleNumberRight; // 单选题答对数量
    private JLabel MutNumberRight; // 多选题答对数量
    private JLabel ValidNumberRight; // 判断题答对数量

    private JLabel scoreLabel;//分数
    private int score = 0;

    private int snr=0;
    private int mnr=0;
    private int vnr=0;

    private JLabel ansLabel;
    private String ans;

    // 问题数组，格式为：
    // {"问题内容", "选项1", "选项2", "选项3", "选项4", "题型（single/multiple/truefalse）", "正确答案（单选/多选为A/B/C/D，判断题为T/F）"}
    private String[][] questions = {
            {"Question 1:1+1=?", "A. 1", "B. 2", "C. 3", "D. 4", "single", "B"},
            {"Question 2: 1+1<?", "A. 1", "B. 2", "C. 3", "D. 4", "multiple", "C,D"},
            {"Question 3: 1+1=1", "A. True", "B. False", "truefalse", "B"},
            {"Question 4: 2+2=?", "A. 1", "B. 2", "C. 3", "D. 4", "single", "D"},
            {"Question 5: ?>4", "A. 5", "B. 4", "C. 6", "D. 7", "multiple", "A,C,D"},
            {"Question 6: 2<3", "A. True", "B. False", "truefalse", "A"},
            {"Question 7: 2x+3=5", "A. x=0", "B. x=1", "C. x=3", "D. x=4", "single", "B"},
            {"Question 8: 2x^2=18", "A. x=-3", "B. x=0", "C. x=3", "D. x=4", "multiple", "A,C"},
            {"Question 9: sin90°<sin180°", "A. True", "B. False", "truefalse", "B"},
            {"Question 10: x=|-3|", "A. 1", "B. 2", "C. 3", "D. -3", "single", "C"},
            {"Question 11: cosx=0", "A. x=0°", "B. x=90°", "C. 180°", "D. 270°", "multiple", "B,D"},
            {"Question 12: x^2>-1", "A. True", "B. False", "truefalse", "A"},
            {"Question 13: 3x=12", "A. 1", "B. 2", "C. 3", "D. 4", "single", "D"},
            {"Question 14: x^3<10", "A. 3", "B. 2", "C. 1", "D. 0", "multiple", "B,C,D"},
            {"Question 15: 10>20", "A. True", "B. False", "truefalse", "B"},
            {"Question 16:1+1=?", "A. 1", "B. 2", "C. 3", "D. 4", "single", "B"},
            {"Question 17: 1+1<?", "A. 1", "B. 2", "C. 3", "D. 4", "multiple", "C,D"},
            {"Question 18: 1+1=1", "A. True", "B. False", "truefalse", "B"},
            {"Question 19: 2+2=?", "A. 1", "B. 2", "C. 3", "D. 4", "single", "D"},
            {"Question 20: ?>4", "A. 5", "B. 4", "C. 6", "D. 7", "multiple", "A,C,D"},
            {"Question 21: 2<3", "A. True", "B. False", "truefalse", "A"},
            {"Question 22: 2x+3=5", "A. x=0", "B. x=1", "C. x=3", "D. x=4", "single", "B"},
            {"Question 23: 2x^2=18", "A. x=-3", "B. x=0", "C. x=3", "D. x=4", "multiple", "A,C"},
            {"Question 24: sin90°<sin180°", "A. True", "B. False", "truefalse", "B"},
            {"Question 25: x=|-3|", "A. 1", "B. 2", "C. 3", "D. -3", "single", "C"},
            {"Question 26: cosx=0", "A. x=0°", "B. x=90°", "C. 180°", "D. 270°", "multiple", "B,D"},
            {"Question 27: x^2>-1", "A. True", "B. False", "truefalse", "A"},
            {"Question 28: 3x=12", "A. 1", "B. 2", "C. 3", "D. 4", "single", "D"},
            {"Question 29: x^3<10", "A. 3", "B. 2", "C. 1", "D. 0", "multiple", "B,C,D"},
            {"Question 30: 10>20", "A. True", "B. False", "truefalse", "B"}
    };

    // 记录总答题时间
    public static int totalTime = 0;

    public giveQuestion() {
        super("Quiz App"); // 窗口标题
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // 关闭窗口时退出程序
        setLayout(new GridLayout(8, 1)); // 设置布局
        this.setBounds(100,100,0,0);
        // 初始化界面组件
        questionLabel = new JLabel();
        add(questionLabel);

        singleChoiceOptions = new JRadioButton[4];
        ButtonGroup singleChoiceButtonGroup = new ButtonGroup();
        for (int i = 0; i < 4; i++) {
            singleChoiceOptions[i] = new JRadioButton();
            singleChoiceButtonGroup.add(singleChoiceOptions[i]);
            add(singleChoiceOptions[i]);
        }

        multipleChoiceOptions = new JCheckBox[4];
        for (int i = 0; i < 4; i++) {
            multipleChoiceOptions[i] = new JCheckBox();
            add(multipleChoiceOptions[i]);
        }

        trueOption = new JRadioButton("True");
        falseOption = new JRadioButton("False");
        ButtonGroup trueFalseButtonGroup = new ButtonGroup();
        trueFalseButtonGroup.add(trueOption);
        trueFalseButtonGroup.add(falseOption);
        add(trueOption);
        add(falseOption);

        submitButton = new JButton("Submit");
        add(submitButton);

        timeLabel = new JLabel("Time left: 20");
        add(timeLabel);

        singleNumber =new JLabel("单选题数量:");
        add(singleNumber);

        MutNumber =new JLabel("多选题数量:");
        add(MutNumber);

        ValidNumber =new JLabel("判断题数量:");
        add(ValidNumber);
        int singleN = 0;
        int mutN = 0;
        int valN = 0;
        for(String[] currentQuestion: questions) {
        	String questionType = currentQuestion.length==7?currentQuestion[5]:currentQuestion[3]; // 获取问题类型
        	if (questionType.equals("single")) {
        		singleN++;
        	} else if (questionType.equals("multiple")) {
        		mutN++;
        	}else {
        		valN++;
        	}
        }
        singleNumber.setText("单选题数量:" + singleN);
        MutNumber.setText("多选题数量:" + mutN);
        ValidNumber.setText("判断题数量:" + valN);

        singleNumberRight =new JLabel("单选题正确数量:0");
        add(singleNumberRight);

        MutNumberRight =new JLabel("多选题正确数量:0");
        add(MutNumberRight);

        ValidNumberRight =new JLabel("判断题正确数量:0");
        add(ValidNumberRight);

        scoreLabel = new JLabel("得分:0");
        add(scoreLabel);

        ansLabel = new JLabel("答案:");
        add(ansLabel);

        // 初始化倒计时器
        timer = new Timer(1000, new ActionListener() {
            int timeLeft = 20;

            @Override
            public void actionPerformed(ActionEvent e) {
                timeLeft--;
                timeLabel.setText("Time left: " + timeLeft);
                if (timeLeft <= 0) {
                    submitAnswer();
                    nextQuestion();
                }
            }
        });

        // 提交按钮点击事件
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                submitAnswer();
                nextQuestion();
            }
        });

        // 显示第一道问题
        showQuestion(0);
    }

    private void showQuestion(int index) {
        String[] currentQuestion = questions[index]; // 当前问题的信息
        questionLabel.setText(currentQuestion[0]); // 显示问题内容
        System.out.println(currentQuestion.length);
        String questionType = currentQuestion.length==7?currentQuestion[5]:currentQuestion[3]; // 获取问题类型
        ansLabel.setText((currentQuestion.length==7?currentQuestion[6]:currentQuestion[4]));
        if (questionType.equals("single")) { // 如果是单选题
            for (int i = 0; i < 4; i++) {
                if (currentQuestion.length > i + 1) {
                    singleChoiceOptions[i].setVisible(true);
                    singleChoiceOptions[i].setText(currentQuestion[i + 1]); // 显示选项内容
                } else {
                    singleChoiceOptions[i].setVisible(false); // 不需要显示的选项隐藏起来
                }
            }
            for (int i = 0; i < 4; i++) {
                multipleChoiceOptions[i].setVisible(false); // 多选和判断题选项都要隐藏
            }
            trueOption.setVisible(false);
            falseOption.setVisible(false);
        } else if (questionType.equals("multiple")) { // 如果是多选题
            for (int i = 0; i < 4; i++) {
                if (currentQuestion.length > i + 1) {
                    multipleChoiceOptions[i].setVisible(true);
                    multipleChoiceOptions[i].setText(currentQuestion[i + 1]);
                    multipleChoiceOptions[i].setSelected(false); // 多选题需要设置初始状态为未选中
                } else {
                    multipleChoiceOptions[i].setVisible(false);
                }
            }
            for (int i = 0; i < 4; i++) {
                singleChoiceOptions[i].setVisible(false);
            }
            trueOption.setVisible(false);
            falseOption.setVisible(false);
        } else if (questionType.equals("truefalse")) { // 如果是判断题
            for (int i = 0; i < 4; i++) {
                singleChoiceOptions[i].setVisible(false);
                multipleChoiceOptions[i].setVisible(false);
            }
            trueOption.setVisible(true);
            falseOption.setVisible(true);
            trueOption.setSelected(false); // 初始状态为未选中
            falseOption.setSelected(false);
        }

        // 重新启动倒计时器
        timer = new Timer(1000, new ActionListener() {
            int timeLeft = 20;

            @Override
            public void actionPerformed(ActionEvent e) {
                timeLeft--;
                timeLabel.setText("Time left: " + timeLeft);
                totalTime++; // 记录答题时间
                //System.out.println("total:" + totalTime);
                if (timeLeft <= 0) {
                    submitAnswer();
                    nextQuestion();
                }
            }
        });
        timer.restart();
    }

    private void submitAnswer() {
        String[] currentQuestion = questions[currentQuestionIndex];
        String questionType = currentQuestion.length==7?currentQuestion[5]:currentQuestion[3];

        if (questionType.equals("single")) { // 如果是单选题
            int selectedOption = -1;
            for (int i = 0; i < 4; i++) {
                if (singleChoiceOptions[i].isSelected()) {
                    selectedOption = i;
                    break;
                }
            }
            if (selectedOption != -1) {
                String selectedAnswer = singleChoiceOptions[selectedOption].getText().substring(0, 1);
                answerResults[currentQuestionIndex] = selectedAnswer.equalsIgnoreCase(currentQuestion[6]); // 判断答案是否正确
                if(selectedAnswer.equalsIgnoreCase(currentQuestion[6])) {
                	snr ++;
                	score++;
                }
            }
        } else if (questionType.equals("multiple")) { // 如果是多选题
            java.util.List<String> selectedOptions = new ArrayList<>();
            for (int i = 0; i < 4; i++) {
                if (multipleChoiceOptions[i].isSelected()) {
                    selectedOptions.add(multipleChoiceOptions[i].getText().substring(0, 1));
                }
            }
            String selectedAnswer = String.join(",", selectedOptions);
            answerResults[currentQuestionIndex] = selectedAnswer.equalsIgnoreCase(currentQuestion[6]);
            if(selectedAnswer.equalsIgnoreCase(currentQuestion[6])) {
            	mnr++;
            	score+=2;
            }
        } else if (questionType.equals("truefalse")) { // 如果是判断题
            if (trueOption.isSelected()) {
                answerResults[currentQuestionIndex] = currentQuestion[4].equalsIgnoreCase("B"); // 判断答案是否正确
                if(currentQuestion[4].equalsIgnoreCase("A")) {
                	vnr++;
                	score++;
                }
            } else if (falseOption.isSelected()) {
                answerResults[currentQuestionIndex] = currentQuestion[4].equalsIgnoreCase("A");
                if(currentQuestion[4].equalsIgnoreCase("B")) {
                	vnr++;
                	score++;
                }
            }
        }

        singleNumberRight.setText("单选题正确数量:" + snr);
        MutNumberRight.setText("多选题正确数量:" + mnr);
        ValidNumberRight.setText("判断题正确数量:" + vnr);
        scoreLabel.setText("分数:" + score);
        timer.stop(); // 停止倒计时器
    }

    private void nextQuestion() {
        timer.stop();
        timeLabel.setText("Time left: 20");
        currentQuestionIndex++;
        if (currentQuestionIndex >= totalQuestions) { // 答完了所有问题，显示结果
            showResult();
        } else { // 显示下一道问题
            showQuestion(currentQuestionIndex);
        }
    }

    private void showResult() {
        getContentPane().removeAll(); // 移除之前的所有组件
        setLayout(new FlowLayout());

        int correctCount = 0;
        for (boolean result : answerResults) {
            if (result) {
                correctCount++;
            }
        }

        JLabel totalQuestionsLabel = new JLabel("Total Questions: " + totalQuestions);
        JLabel totalscore =new JLabel("Total Scores:"+score);
        JLabel correctQuestionsLabel = new JLabel("Correct Answers: " + (vnr+mnr+snr));
        JLabel totalTimeLabel = new JLabel("Total Time: " + totalTime + " seconds");

        add(totalQuestionsLabel);
        add(totalscore);
        add(correctQuestionsLabel);
        add(totalTimeLabel);

        pack(); // 自适应大小
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                giveQuestion g = new giveQuestion();
                g.setSize(500, 400);
                g.setVisible(true);
            }
        });
    }
}
