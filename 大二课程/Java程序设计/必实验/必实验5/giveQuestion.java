import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;

public class giveQuestion extends JFrame{
    // �����������
    private JLabel questionLabel; // ��ʾ����ı�ǩ
    private JRadioButton[] singleChoiceOptions; // ��ѡ��ѡ��
    private JCheckBox[] multipleChoiceOptions; // ��ѡ��ѡ��
    private JRadioButton trueOption, falseOption; // �ж���ѡ��
    private JButton submitButton; // �ύ��ť
    private JLabel timeLabel; // ����ʱ��ǩ
    private Timer timer; // ����ʱ��

    // ������ر���
    private int currentQuestionIndex = 0; // ��ǰ���������
    private int totalQuestions = 15; // ��������
    private boolean[] answerResults = new boolean[totalQuestions]; // ��¼ÿ������Ĵ��Ƿ���ȷ

    private JLabel singleNumber; // ��ѡ������
    private JLabel MutNumber; // ��ѡ������
    private JLabel ValidNumber; // �ж�������

    private JLabel singleNumberRight; // ��ѡ��������
    private JLabel MutNumberRight; // ��ѡ��������
    private JLabel ValidNumberRight; // �ж���������

    private JLabel scoreLabel;//����
    private int score = 0;

    private int snr=0;
    private int mnr=0;
    private int vnr=0;

    private JLabel ansLabel;
    private String ans;

    // �������飬��ʽΪ��
    // {"��������", "ѡ��1", "ѡ��2", "ѡ��3", "ѡ��4", "���ͣ�single/multiple/truefalse��", "��ȷ�𰸣���ѡ/��ѡΪA/B/C/D���ж���ΪT/F��"}
    private String[][] questions = {
            {"Question 1:1+1=?", "A. 1", "B. 2", "C. 3", "D. 4", "single", "B"},
            {"Question 2: 1+1<?", "A. 1", "B. 2", "C. 3", "D. 4", "multiple", "C,D"},
            {"Question 3: 1+1=1", "A. True", "B. False", "truefalse", "B"},
            {"Question 4: 2+2=?", "A. 1", "B. 2", "C. 3", "D. 4", "single", "D"},
            {"Question 5: ?>4", "A. 5", "B. 4", "C. 6", "D. 7", "multiple", "A,C,D"},
            {"Question 6: 2<3", "A. True", "B. False", "truefalse", "A"},
            {"Question 7: 2x+3=5", "A. x=0", "B. x=1", "C. x=3", "D. x=4", "single", "B"},
            {"Question 8: 2x^2=18", "A. x=-3", "B. x=0", "C. x=3", "D. x=4", "multiple", "A,C"},
            {"Question 9: sin90��<sin180��", "A. True", "B. False", "truefalse", "B"},
            {"Question 10: x=|-3|", "A. 1", "B. 2", "C. 3", "D. -3", "single", "C"},
            {"Question 11: cosx=0", "A. x=0��", "B. x=90��", "C. 180��", "D. 270��", "multiple", "B,D"},
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
            {"Question 24: sin90��<sin180��", "A. True", "B. False", "truefalse", "B"},
            {"Question 25: x=|-3|", "A. 1", "B. 2", "C. 3", "D. -3", "single", "C"},
            {"Question 26: cosx=0", "A. x=0��", "B. x=90��", "C. 180��", "D. 270��", "multiple", "B,D"},
            {"Question 27: x^2>-1", "A. True", "B. False", "truefalse", "A"},
            {"Question 28: 3x=12", "A. 1", "B. 2", "C. 3", "D. 4", "single", "D"},
            {"Question 29: x^3<10", "A. 3", "B. 2", "C. 1", "D. 0", "multiple", "B,C,D"},
            {"Question 30: 10>20", "A. True", "B. False", "truefalse", "B"}
    };

    // ��¼�ܴ���ʱ��
    public static int totalTime = 0;

    public giveQuestion() {
        super("Quiz App"); // ���ڱ���
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // �رմ���ʱ�˳�����
        setLayout(new GridLayout(8, 1)); // ���ò���
        this.setBounds(100,100,0,0);
        // ��ʼ���������
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

        singleNumber =new JLabel("��ѡ������:");
        add(singleNumber);

        MutNumber =new JLabel("��ѡ������:");
        add(MutNumber);

        ValidNumber =new JLabel("�ж�������:");
        add(ValidNumber);
        int singleN = 0;
        int mutN = 0;
        int valN = 0;
        for(String[] currentQuestion: questions) {
        	String questionType = currentQuestion.length==7?currentQuestion[5]:currentQuestion[3]; // ��ȡ��������
        	if (questionType.equals("single")) {
        		singleN++;
        	} else if (questionType.equals("multiple")) {
        		mutN++;
        	}else {
        		valN++;
        	}
        }
        singleNumber.setText("��ѡ������:" + singleN);
        MutNumber.setText("��ѡ������:" + mutN);
        ValidNumber.setText("�ж�������:" + valN);

        singleNumberRight =new JLabel("��ѡ����ȷ����:0");
        add(singleNumberRight);

        MutNumberRight =new JLabel("��ѡ����ȷ����:0");
        add(MutNumberRight);

        ValidNumberRight =new JLabel("�ж�����ȷ����:0");
        add(ValidNumberRight);

        scoreLabel = new JLabel("�÷�:0");
        add(scoreLabel);

        ansLabel = new JLabel("��:");
        add(ansLabel);

        // ��ʼ������ʱ��
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

        // �ύ��ť����¼�
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                submitAnswer();
                nextQuestion();
            }
        });

        // ��ʾ��һ������
        showQuestion(0);
    }

    private void showQuestion(int index) {
        String[] currentQuestion = questions[index]; // ��ǰ�������Ϣ
        questionLabel.setText(currentQuestion[0]); // ��ʾ��������
        System.out.println(currentQuestion.length);
        String questionType = currentQuestion.length==7?currentQuestion[5]:currentQuestion[3]; // ��ȡ��������
        ansLabel.setText((currentQuestion.length==7?currentQuestion[6]:currentQuestion[4]));
        if (questionType.equals("single")) { // ����ǵ�ѡ��
            for (int i = 0; i < 4; i++) {
                if (currentQuestion.length > i + 1) {
                    singleChoiceOptions[i].setVisible(true);
                    singleChoiceOptions[i].setText(currentQuestion[i + 1]); // ��ʾѡ������
                } else {
                    singleChoiceOptions[i].setVisible(false); // ����Ҫ��ʾ��ѡ����������
                }
            }
            for (int i = 0; i < 4; i++) {
                multipleChoiceOptions[i].setVisible(false); // ��ѡ���ж���ѡ�Ҫ����
            }
            trueOption.setVisible(false);
            falseOption.setVisible(false);
        } else if (questionType.equals("multiple")) { // ����Ƕ�ѡ��
            for (int i = 0; i < 4; i++) {
                if (currentQuestion.length > i + 1) {
                    multipleChoiceOptions[i].setVisible(true);
                    multipleChoiceOptions[i].setText(currentQuestion[i + 1]);
                    multipleChoiceOptions[i].setSelected(false); // ��ѡ����Ҫ���ó�ʼ״̬Ϊδѡ��
                } else {
                    multipleChoiceOptions[i].setVisible(false);
                }
            }
            for (int i = 0; i < 4; i++) {
                singleChoiceOptions[i].setVisible(false);
            }
            trueOption.setVisible(false);
            falseOption.setVisible(false);
        } else if (questionType.equals("truefalse")) { // ������ж���
            for (int i = 0; i < 4; i++) {
                singleChoiceOptions[i].setVisible(false);
                multipleChoiceOptions[i].setVisible(false);
            }
            trueOption.setVisible(true);
            falseOption.setVisible(true);
            trueOption.setSelected(false); // ��ʼ״̬Ϊδѡ��
            falseOption.setSelected(false);
        }

        // ������������ʱ��
        timer = new Timer(1000, new ActionListener() {
            int timeLeft = 20;

            @Override
            public void actionPerformed(ActionEvent e) {
                timeLeft--;
                timeLabel.setText("Time left: " + timeLeft);
                totalTime++; // ��¼����ʱ��
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

        if (questionType.equals("single")) { // ����ǵ�ѡ��
            int selectedOption = -1;
            for (int i = 0; i < 4; i++) {
                if (singleChoiceOptions[i].isSelected()) {
                    selectedOption = i;
                    break;
                }
            }
            if (selectedOption != -1) {
                String selectedAnswer = singleChoiceOptions[selectedOption].getText().substring(0, 1);
                answerResults[currentQuestionIndex] = selectedAnswer.equalsIgnoreCase(currentQuestion[6]); // �жϴ��Ƿ���ȷ
                if(selectedAnswer.equalsIgnoreCase(currentQuestion[6])) {
                	snr ++;
                	score++;
                }
            }
        } else if (questionType.equals("multiple")) { // ����Ƕ�ѡ��
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
        } else if (questionType.equals("truefalse")) { // ������ж���
            if (trueOption.isSelected()) {
                answerResults[currentQuestionIndex] = currentQuestion[4].equalsIgnoreCase("B"); // �жϴ��Ƿ���ȷ
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

        singleNumberRight.setText("��ѡ����ȷ����:" + snr);
        MutNumberRight.setText("��ѡ����ȷ����:" + mnr);
        ValidNumberRight.setText("�ж�����ȷ����:" + vnr);
        scoreLabel.setText("����:" + score);
        timer.stop(); // ֹͣ����ʱ��
    }

    private void nextQuestion() {
        timer.stop();
        timeLabel.setText("Time left: 20");
        currentQuestionIndex++;
        if (currentQuestionIndex >= totalQuestions) { // �������������⣬��ʾ���
            showResult();
        } else { // ��ʾ��һ������
            showQuestion(currentQuestionIndex);
        }
    }

    private void showResult() {
        getContentPane().removeAll(); // �Ƴ�֮ǰ���������
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

        pack(); // ����Ӧ��С
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
