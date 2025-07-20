import java.util.InputMismatchException;
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner in=new Scanner(System.in);
        String menu="北京烤鸭：199.1元；西芹炒肉：11.8元；酸菜鱼：59.1元；铁板牛柳：33.1元";
        Scanner scanner=new Scanner(menu);
        scanner.useDelimiter("[^0123456789.]+");
        double tot=0;
        while (scanner.hasNext()){
            try {
                tot+=scanner.nextDouble();
            }
            catch (InputMismatchException exp){
                String t=scanner.next();
            }
        }
        System.out.println("总价格："+tot+"元");
    }
}