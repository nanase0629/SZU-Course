class Bank{
    private int money=10000;
    public synchronized void Withdraw(String s,int b){
        if(s=="withdraw"){
            while (money>0){
                try {
                    if(money>b){
                        money-=b;
                        System.out.println("取款成功,取款金额为:"+b+"元,余额为:"+money+"元");
                        notifyAll();
                        wait();
                    }
                    else {
                        System.out.println("取款失败,余额不足");
                        notifyAll();
                        break;

                    }
                }
                catch (InterruptedException ex){
                    System.out.println("请等待取钱完成");
                }
            }
            notifyAll();
        }
    }
}
class  WithdrawThread implements Runnable {
    private Bank bank;
    private String s;
    private int b;

    public WithdrawThread(String s, int b,Bank b2) {
        bank=b2;
        this.s = s;
        this.b = b;
    }
    @Override
    public void run(){
        if(Thread.currentThread().getName().equals(s)){
            bank.Withdraw(s,b);
        }
    }
}
public class Main {
    public static void main(String[] args) {
        Bank bb=new Bank();
        Thread t1=new Thread(new WithdrawThread("withdraw",200,bb));
        Thread t2=new Thread(new WithdrawThread("withdraw",100,bb));
        t1.setName("withdraw");
        t2.setName("withdraw");
        t1.start();
        t2.start();
    }
}