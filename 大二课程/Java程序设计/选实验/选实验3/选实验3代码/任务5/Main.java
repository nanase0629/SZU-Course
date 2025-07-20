import java.util.Scanner;
class BinaryFormatException  extends Exception{
    BinaryFormatException(String message){
        super(message);
    }

}
public class Main {
    public static void main(String[] args) {
        Scanner in= new Scanner(System.in);
        System.out.println("请输入一个二进制字符串：");
        String str=in.next();
        try{
            int tmp=bin2Dec(str);
            System.out.println(tmp);
        }
        catch (BinaryFormatException ec){
            ec.printStackTrace();
        }
    }
    public static int bin2Dec(String binaryString)throws BinaryFormatException {
        if(!binaryString.matches("^[01]+$")){
            throw new BinaryFormatException("不是二进制数字");
        }
        return Integer.parseInt(binaryString,2);
    }
    /*public static int bin2Dec(String binaryString){
        if(!binaryString.matches("^[01]+$")){
            throw  new NumberFormatException("不是二进制数字");
        }
        return Integer.parseInt(binaryString,2);
    }*/
}