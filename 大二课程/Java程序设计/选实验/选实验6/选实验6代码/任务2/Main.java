import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Random;

public class Main {
    public static void main(String[] args) {
        File file=new File("Exercisel_02.dat");
        if(!file.exists()){
            try {
                file.createNewFile();
            }catch (IOException e){}
        }
        Random random=new Random();
       try (FileOutputStream output=new FileOutputStream("Exercisel_02.dat")) {
           for (int i = 0; i < 20; i++) {
               output.write(random.nextInt(100));
           }
       }catch (IOException e){}
       try (FileInputStream input=new FileInputStream("Exercisel_02.dat")) {
           int value;
           while ((value = input.read()) != -1) {
               System.out.print(value+" ");
           }
           System.out.println();
           input.close();
       }catch (IOException e){}

    }
}