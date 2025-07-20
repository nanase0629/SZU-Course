package com.youdao.aicloud.translate;
import javax.swing.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import com.youdao.aicloud.translate.utils.AuthV3Util;
import com.youdao.aicloud.translate.utils.HttpUtil;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;

class SentenceTranslationDemo extends JFrame{
    public JTextArea textArea;
    String Intext;
    String Translate_baidu;
    String Translate_youdao;
    String Common_both;
    SentenceTranslationDemo() {
        textArea=new JTextArea();

        JFrame frame = new JFrame("Sentence Translation Demo");
        frame.setBounds(100, 100, 540, 450);
        frame.setVisible(true);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.getContentPane().setLayout(null);

        JLabel englishLabel = new JLabel("English Sentence:");
        englishLabel.setBounds(10, 10, 150, 20);
        frame.getContentPane().add(englishLabel);

        textArea = new JTextArea();
        textArea.setBounds(10, 40, 300, 100);
        frame.getContentPane().add(textArea);

        JLabel baiduLabel = new JLabel("Translation (百度)");
        baiduLabel.setBounds(10, 160, 150, 20);
        frame.getContentPane().add(baiduLabel);

        JTextArea englishTranslationTextArea = new JTextArea();
        englishTranslationTextArea.setBounds(10, 190, 245, 100);
        frame.getContentPane().add(englishTranslationTextArea);

        JLabel youdaoLabel = new JLabel("Translation (有道)");
        youdaoLabel.setBounds(260, 160, 150, 20);
        frame.getContentPane().add(youdaoLabel);

        JTextArea englishTranslationTextArea2 = new JTextArea();
        englishTranslationTextArea2.setBounds(260, 190, 255, 100);
        frame.getContentPane().add(englishTranslationTextArea2);

        JLabel commonLabel = new JLabel("Common Translation");
        commonLabel.setBounds(10, 310, 150, 20);
        frame.getContentPane().add(commonLabel);

        JTextArea commonTextArea = new JTextArea();
        commonTextArea.setBounds(10, 340, 500, 50);
        frame.getContentPane().add(commonTextArea);

        JButton button = new JButton("Translate");
        button.setBounds(350, 40, 100, 30);
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String input = textArea.getText();
                Intext=input;
                //System.out.println(Intext);
                Main main = new Main();
                Translate_baidu=main.Show(SentenceTranslationDemo.this);
                try {
                    Translate_youdao=main.Show2(SentenceTranslationDemo.this);
                } catch (NoSuchAlgorithmException ex) {
                    throw new RuntimeException(ex);
                }
                Translate_youdao=Translate_youdao.replaceAll("[^\\u4e00-\\u9fa5]","");
                //System.out.println(Intext+'\n'+Translate_baidu+'\n'+Translate_youdao);
                englishTranslationTextArea.setText(Translate_baidu);
                englishTranslationTextArea2.setText(Translate_youdao);;


                Set<Character>set1 =new HashSet<>();
                Set<Character>set2 =new HashSet<>();
                for(char c:Translate_baidu.toCharArray()){
                    set1.add(c);
                }
                for(char c:Translate_youdao.toCharArray()){
                    set2.add(c);
                }
                set1.retainAll(set2);
                StringBuilder sb=new StringBuilder();
                for(Character c:set1){
                    sb.append(c);
                    sb.append(' ');
                }
                Common_both=sb.toString();
                commonTextArea.setText(Common_both);
            }
        });
        frame.getContentPane().add(button);
        frame.repaint();



    }
    String Result(){
        return Intext;
    }
}

public class Main {
    //百度
    private static final String APP_ID = "20231211001907288";
    private static final String SECURITY_KEY = "L0fUxzArKIFYTqHFKTzX";
    public static String unicodeDecode(String string) {
        Pattern pattern = Pattern.compile("(\\\\u(\\p{XDigit}{4}))");
        Matcher matcher = pattern.matcher(string);
        char ch;
        while (matcher.find()) {
            ch = (char) Integer.parseInt(matcher.group(2), 16);
            string = string.replace(matcher.group(1), ch + "");
        }
        return string;
    }
    String Show(SentenceTranslationDemo s){
        TransApi api = new TransApi(APP_ID, SECURITY_KEY);
        String query = s.Result();
        String result = api.getTransResult(query, "auto", "zh");
        System.out.println(result);
        int begin = result.indexOf("dst");
        String en = result.substring(begin + 6, result.length() - 4);
        en=unicodeDecode(en);
        return en;
    }
    //有道
    private static final String APP_KEY = "1466aa8a58016a30";     // 您的应用ID
    private static final String APP_SECRET = "vVnaDRHP7j8Nv6OoO8u0gMTjNlBHQmgQ";  // 您的应用密钥

    private static Map<String, String[]> createRequestParams(SentenceTranslationDemo s) {
        String q = s.Result();
        String from = "en";
        String to = "zh-CHS";
        String vocabId = "aaa";

        return new HashMap<String, String[]>() {{
            put("q", new String[]{q});
            put("from", new String[]{from});
            put("to", new String[]{to});
            put("vocabId", new String[]{vocabId});
        }};
    }
    String Show2(SentenceTranslationDemo s) throws NoSuchAlgorithmException {
        Map<String, String[]> params = createRequestParams(s);
        // 添加鉴权相关参数
        AuthV3Util.addAuthParams(APP_KEY, APP_SECRET, params);
        // 请求api服务
        byte[] result = HttpUtil.doPost("https://openapi.youdao.com/api", null, params, "application/json");

        // 打印返回结果
        String r=new String(result);
        return r;

    }

    public static void main(String[] agrs) {
        SentenceTranslationDemo s=new SentenceTranslationDemo();
    }
}