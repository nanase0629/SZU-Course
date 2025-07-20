import java.util.Scanner;
import java.util.*;
public class Main {
    public static void main(String[] args) {
        String text ="About Shenzhen University (SZU) is committed to excellence in teaching, research and social service. Sticking to the motto of “self-reliance, self-discipline, self-improvement”, the University is dedicated to serving the Shenzhen Special Economic Zone (SEZ), demonstrating China’s reform and opening up and pioneering change in higher education.\n" +
                "\n" +
                "SZU, which is based in Shenzhen, China’s first Special Economic Zone and a key city in the Guangdong-Hong Kong-Macau Greater Bay Area, is distinctively known as an Experimental University in higher education with its reforms in the sector acknowledged in Mainland China.\n" +
                "\n" +
                "Established in 1983, SZU received support from top Chinese universities including Peking University, Tsinghua University and Renmin University of China in the founding of new schools. In the past decades, the University has undergone rapid growth and has become a comprehensive university with complete disciplines, top-ranked academic and research institutes and awe-inspiring faculty. SZU faculty members are engaged with teaching and research for the betterment of society. They are devoted to seeking solutions to pressing global challenges and promoting innovation.\n" +
                "\n" +
                "SZU offers a wide array of undergraduate and graduate programs and provides students with an interdisciplinary and inclusive multicultural learning environment. Students in SZU enjoy the plenty resources and facilities of both the SEZ and the University, pursue academic excellence and discover new interests and opportunities in a fast-changing era.\n" +
                "\n" +
                "SZU is an integral part of the SEZ, a thriving technology and innovation hub. With two campuses in Yuehai and Lihu, the University vigorously conducts leading researches in various fields and collaborates with high-tech enterprises in the community for technology transfer. SZU strives to provide a high-quality and effective education and develop in each SZU member the ability and passion to innovate and contribute to social progress and development, and encourages talented young people to start entrepreneurship in SZU. Our alumni including Tencent have founded dozens of innovative companies with significant influence.\n" +
                "\n" +
                "SZU is accelerating its pace toward internationalization, providing a variety of global learning opportunities. The University has established partnerships with numbers of overseas universities to offer exceptional exchange programs, joint degree programs, research collaborations, and a variety of other forms of collaborations with international partners. Students from all over the world are welcomed in SZU. In the city noted for its urban vitality and natural beauty, students can explore the most attractive parts of China, pursue their passion and develop their interests, perspectives and abilities.";

        // 将文本转换为小写，并使用空格分割为单词数组
        String[] words = text.toLowerCase().split(" ");

        // 统计每个单词的出现次数
        Map<String, Integer> wordCounts = new HashMap<>();
        for (String word : words) {
            wordCounts.put(word, wordCounts.getOrDefault(word, 0) + 1);
        }

        // 根据出现次数排序
        List<Map.Entry<String, Integer>> sortedWordCounts = new ArrayList<>(wordCounts.entrySet());
        sortedWordCounts.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        // 输出出现次数最多的50个单词
        int count = 0;
        for (Map.Entry<String, Integer> entry : sortedWordCounts) {
            System.out.print(entry.getKey() + ":" + entry.getValue() + " ");
            count++;
            if (count % 10 == 0) {
                System.out.println();
            }
            if (count == 50) {
                break;
            }
        }
    }
}

