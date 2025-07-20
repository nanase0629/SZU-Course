import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner in=new Scanner(System.in);
       for(int i=0;i<10;i++){
           System.out.println("请输入第"+(i+1)+"个字符串");
           String s=in.next();
           String big=new String();
           String small=new String();
           String num=new String();
           for(char c:s.toCharArray()){
               if(c>='A'&&c<='Z')big+=c;
               else if(c>='a'&&c<='z')small+=c;
               else if(c>='0'&&c<='9')num+=c;
           }
           System.out.println("大写英文字母包括："+big);
           System.out.println("小写英文字母包括："+small);
           System.out.println("数字包括："+num);
       }
    }
}