import java.text.ParseException;
import java.util.Date;
import java.util.Scanner;
import java.text.SimpleDateFormat;
public class Main {
    public static void main(String[] args) throws ParseException {
        Scanner in= new Scanner(System.in);
        SimpleDateFormat sdf=new SimpleDateFormat("yyyy年MM月dd日HH时mm分ss秒");
        Date[] times=new Date[6];

        for(int i=1;i<=5;i++){
            System.out.println("请输入第"+i+"个时间:");
             String s=in.next();
             times[i]=sdf.parse(s);
        }
        System.out.println("以下为相邻时间计算结果：");
        for (int i=2;i<=5;i++){
            System.out.println(times[i]);
            long t=times[i].getTime()-times[i-1].getTime();
            long days = t/ (1000 * 60 * 60 * 24);
            long hours = (t% (1000 * 60 * 60 * 24)) / (1000 * 60 * 60);
            long minutes = (t % (1000 * 60 * 60)) / (1000 * 60);
            long seconds = (t% (1000 * 60)) / 1000;
            System.out.println(days+"日"+hours+"时"+minutes+"分"+seconds+"秒");
        }
    }
}