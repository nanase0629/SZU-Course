class  Month {
    private int num=1;
    private int num1=0;
    private String[]str={"One January","Two February","Three March","Four April","Five May","Six June","Seven July","Eight August","Nine September","Ten October","Eleven November","Twelve December"};
    public synchronized void show(String s) {
        if (s == "num") {
            while (num<=12) {
                try {
                    System.out.print(num++);
                    notifyAll();
                    wait();
                } catch (InterruptedException ex) {}
            }
        }
        else if(s=="month"){
            while (num1<12) {
                try {
                    System.out.println(str[num1]);
                    num1++;
                    notifyAll();
                    wait();

                } catch (InterruptedException ex) {}
            }
        }
        notifyAll();
    }
}
class Use implements Runnable{
    Month m=new Month();
    String name1,name2;
    Use(String s1,String s2){
        name1=s1;
        name2=s2;
    }

    @Override
    public void run(){
        if (Thread.currentThread().getName().equals(name1)) {
            m.show("num");
        }
        else if(Thread.currentThread().getName().equals(name2)) {
            m.show("month");
        }
    }
}
public class Main {
    public static void main(String[] args) {
        Use m=new Use("num","month");
        Thread thread1 =new Thread(m);
        Thread thread2 =new Thread(m);
        thread1.setName("num");
        thread2.setName("month");
        thread1.start();
        thread2.start();
    }
}