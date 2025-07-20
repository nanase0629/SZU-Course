abstract class Human{
   public String name;
   public Human(String name){
       this.name=name;
    }
    public Human(){}
    public abstract  double sayHello();
}
class Chinese extends Human{
    public Chinese(String name){
        super(name);
    }
    @Override
    public double sayHello() {
        System.out.println(name+":你好我是中文");
        return 0;
    }
}
class French extends Human{
    public French(String name){
        super(name);
    }
    @Override
    public double sayHello() {
        System.out.println(name+":你好我是法语");
        return 0;
    }
}
class Japanese extends Human{
    public Japanese(String name){
        super(name);
    }
    @Override
    public double sayHello() {
        System.out.println(name+":你好我是日语");
        return 0;
    }
}
class HumanTest{
  public Human h[];
  HumanTest(String c,String f,String j){
      h=new Human[4];
    h[1]=new Chinese(c);
    h[2]=new French(f);
    h[3]=new Japanese(j);
  }
   public void show(){
        for(int i=1;i<=3;i++){
            h[i].sayHello();
        }

   }
}

public class Main {
    public static void main(String[] args) {
        HumanTest ht=new HumanTest("c","f","j");
        ht.show();
    }
}