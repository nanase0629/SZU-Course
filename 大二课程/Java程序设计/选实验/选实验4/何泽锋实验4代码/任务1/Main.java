import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        List<String> A = new ArrayList<>();
        List<String> B = new ArrayList<>();
        List<String> both_in = new ArrayList<>();
        System.out.println("请输入A社团人数：");
        int size_A =in.nextInt();
        for(int i=0;i<size_A;i++){
            String tmp =in.next();
            A.add(tmp);
        }
        System.out.println("请输入B社团人数：");
        int size_B =in.nextInt();
        for(int i=0;i<size_B;i++){
            String tmp =in.next();
            B.add(tmp);
        }
        for(String member:A){
            if(B.contains(member)&&!both_in.contains(member))both_in.add(member);
        }
        System.out.println("参加A社团的人：");
        for(String i:A){
            System.out.println(i);
        }
        System.out.println("参加B社团的人：");
        for(String i:B){
            System.out.println(i);
        }
        System.out.println("同时参加A和B社团的人：");
        for(String i:both_in){
            System.out.println(i);
        }
    }
}